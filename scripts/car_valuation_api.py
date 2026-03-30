#!/usr/bin/env python3
"""
Car Valuation API - Production System
Robust Apify integration for Israeli vehicle data collection
"""

import os
import json
import time
import csv
import requests
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import concurrent.futures
from dataclasses import dataclass

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/home/omer/.openclaw/workspace/car_valuation.log'),
        logging.StreamHandler()
    ]
)

@dataclass
class VehicleQuery:
    """Configuration for a vehicle collection query"""
    manufacturer: str
    model: str
    min_year: int
    max_year: int
    area: str
    max_items: int = 50
    max_km: Optional[int] = None
    min_price: Optional[int] = None
    max_price: Optional[int] = None

@dataclass
class CollectionStats:
    """Statistics for data collection run"""
    total_vehicles: int = 0
    successful_queries: int = 0
    failed_queries: int = 0
    total_cost_usd: float = 0.0
    start_time: datetime = None
    end_time: datetime = None
    
    def duration_minutes(self) -> float:
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds() / 60
        return 0

class CarValuationAPI:
    """Production API for Israeli car valuation data collection"""
    
    def __init__(self, api_token: str):
        self.api_token = api_token
        self.base_url = "https://api.apify.com/v2"
        self.scraper_id = "swerve~yad2-vehicles"
        self.cost_per_1000_results = 5.0  # USD
        
        # Rate limiting
        self.max_concurrent_requests = 3
        self.delay_between_requests = 2.0  # seconds
        
        # Data validation
        self.min_price_threshold = 10000  # ILS
        self.max_price_threshold = 500000  # ILS
        
        self.logger = logging.getLogger(__name__)
        
    def get_israeli_vehicle_queries(self) -> List[VehicleQuery]:
        """Get predefined queries for popular Israeli market vehicles"""
        return [
            # Honda models
            VehicleQuery("Honda", "Civic", 2015, 2020, "tel aviv", 50),
            VehicleQuery("Honda", "Civic", 2015, 2020, "center", 50),
            VehicleQuery("Honda", "Accord", 2015, 2020, "tel aviv", 30),
            
            # Toyota models  
            VehicleQuery("Toyota", "Corolla", 2015, 2020, "tel aviv", 50),
            VehicleQuery("Toyota", "Corolla", 2015, 2020, "center", 50),
            VehicleQuery("Toyota", "Camry", 2015, 2020, "tel aviv", 30),
            
            # Hyundai models
            VehicleQuery("Hyundai", "i30", 2015, 2020, "tel aviv", 50),
            VehicleQuery("Hyundai", "i30", 2015, 2020, "center", 50),
            VehicleQuery("Hyundai", "Elantra", 2015, 2020, "tel aviv", 30),
        ]
    
    def create_apify_input(self, query: VehicleQuery) -> Dict:
        """Convert VehicleQuery to Apify input format"""
        input_data = {
            "vehicleType": "cars",
            "manufacturer": query.manufacturer,
            "model": query.model,
            "minYear": query.min_year,
            "maxYear": query.max_year,
            "area": query.area.lower(),
            "maxItems": query.max_items
        }
        
        if query.max_km:
            input_data["maxKm"] = query.max_km
        if query.min_price:
            input_data["minPrice"] = query.min_price
        if query.max_price:
            input_data["maxPrice"] = query.max_price
            
        return input_data
    
    def run_single_query(self, query: VehicleQuery) -> Tuple[List[Dict], str]:
        """Execute a single vehicle collection query"""
        query_name = f"{query.manufacturer} {query.model} {query.min_year}-{query.max_year} ({query.area})"
        self.logger.info(f"🔍 Starting query: {query_name}")
        
        try:
            # Create and start scraper run
            input_data = self.create_apify_input(query)
            run_id = self._start_scraper_run(input_data)
            
            if not run_id:
                return [], f"Failed to start scraper for {query_name}"
            
            # Monitor run completion
            success = self._monitor_run(run_id)
            if not success:
                return [], f"Scraper run failed for {query_name}"
            
            # Get results
            results = self._get_run_results(run_id)
            self.logger.info(f"✅ Query complete: {query_name} - {len(results)} vehicles")
            
            return results, ""
            
        except Exception as e:
            error_msg = f"Error in query {query_name}: {str(e)}"
            self.logger.error(error_msg)
            return [], error_msg
    
    def _start_scraper_run(self, input_data: Dict) -> Optional[str]:
        """Start an Apify scraper run"""
        url = f"{self.base_url}/acts/{self.scraper_id}/runs"
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(url, json=input_data, headers=headers)
            if response.status_code == 201:
                return response.json()['data']['id']
            else:
                self.logger.error(f"Failed to start scraper: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            self.logger.error(f"Exception starting scraper: {e}")
            return None
    
    def _monitor_run(self, run_id: str, timeout_minutes: int = 10) -> bool:
        """Monitor scraper run until completion"""
        url = f"{self.base_url}/acts/{self.scraper_id}/runs/{run_id}"
        headers = {"Authorization": f"Bearer {self.api_token}"}
        
        start_time = time.time()
        timeout_seconds = timeout_minutes * 60
        
        while time.time() - start_time < timeout_seconds:
            try:
                response = requests.get(url, headers=headers)
                if response.status_code == 200:
                    run_info = response.json()
                    status = run_info['data']['status']
                    
                    if status == "SUCCEEDED":
                        return True
                    elif status == "FAILED":
                        error_msg = run_info['data'].get('statusMessage', 'No error details')
                        self.logger.error(f"Scraper run {run_id} failed: {error_msg}")
                        return False
                    elif status in ["RUNNING", "READY"]:
                        time.sleep(10)  # Check every 10 seconds
                        continue
                    else:
                        self.logger.warning(f"Unknown status for run {run_id}: {status}")
                        time.sleep(10)
                        
            except Exception as e:
                self.logger.error(f"Error monitoring run {run_id}: {e}")
                time.sleep(10)
        
        self.logger.error(f"Run {run_id} timed out after {timeout_minutes} minutes")
        return False
    
    def _get_run_results(self, run_id: str) -> List[Dict]:
        """Get results from completed scraper run"""
        # First get run info to find dataset ID
        run_url = f"{self.base_url}/acts/{self.scraper_id}/runs/{run_id}"
        headers = {"Authorization": f"Bearer {self.api_token}"}
        
        try:
            response = requests.get(run_url, headers=headers)
            if response.status_code == 200:
                run_info = response.json()
                dataset_id = run_info['data'].get('defaultDatasetId')
                
                if dataset_id:
                    return self._get_dataset_results(dataset_id)
        
        except Exception as e:
            self.logger.error(f"Error getting run info for {run_id}: {e}")
        
        return []
    
    def _get_dataset_results(self, dataset_id: str) -> List[Dict]:
        """Get results from dataset"""
        url = f"{self.base_url}/datasets/{dataset_id}/items"
        headers = {"Authorization": f"Bearer {self.api_token}"}
        
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                return response.json()
            else:
                self.logger.error(f"Failed to get dataset {dataset_id}: {response.status_code}")
        except Exception as e:
            self.logger.error(f"Error getting dataset results {dataset_id}: {e}")
        
        return []
    
    def validate_vehicle_data(self, vehicles: List[Dict]) -> List[Dict]:
        """Validate and clean vehicle data"""
        validated = []
        
        for vehicle in vehicles:
            try:
                # Check required fields
                required_fields = ['price', 'year', 'manufacturerEn', 'modelEn']
                if not all(field in vehicle and vehicle[field] for field in required_fields):
                    continue
                
                # Validate price range
                price = vehicle.get('price', 0)
                if not (self.min_price_threshold <= price <= self.max_price_threshold):
                    continue
                
                # Validate year
                year = vehicle.get('year', 0)
                if not (2010 <= year <= 2025):
                    continue
                
                # Clean and standardize data
                vehicle['price'] = int(price)
                vehicle['year'] = int(year)
                vehicle['km'] = int(vehicle.get('km', 0)) if vehicle.get('km') else 0
                
                # Add data quality score
                quality_score = self._calculate_quality_score(vehicle)
                vehicle['data_quality_score'] = quality_score
                
                validated.append(vehicle)
                
            except Exception as e:
                self.logger.warning(f"Error validating vehicle: {e}")
                continue
        
        return validated
    
    def _calculate_quality_score(self, vehicle: Dict) -> float:
        """Calculate data quality score (0-1) based on completeness"""
        important_fields = [
            'price', 'year', 'km', 'manufacturerEn', 'modelEn', 
            'cityEn', 'engineVolume', 'horsePower', 'testDate'
        ]
        
        score = 0
        for field in important_fields:
            if field in vehicle and vehicle[field]:
                score += 1
        
        return score / len(important_fields)
    
    def collect_all_vehicles(self, queries: Optional[List[VehicleQuery]] = None) -> Tuple[List[Dict], CollectionStats]:
        """Collect vehicles from multiple queries with parallel processing"""
        if queries is None:
            queries = self.get_israeli_vehicle_queries()
        
        stats = CollectionStats(start_time=datetime.now())
        all_vehicles = []
        errors = []
        
        self.logger.info(f"🚀 Starting collection of {len(queries)} queries")
        
        # Process queries with controlled concurrency
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_concurrent_requests) as executor:
            future_to_query = {
                executor.submit(self.run_single_query, query): query 
                for query in queries
            }
            
            for future in concurrent.futures.as_completed(future_to_query):
                query = future_to_query[future]
                
                try:
                    vehicles, error = future.result()
                    
                    if error:
                        errors.append(f"{query.manufacturer} {query.model}: {error}")
                        stats.failed_queries += 1
                    else:
                        # Validate and clean data
                        validated_vehicles = self.validate_vehicle_data(vehicles)
                        all_vehicles.extend(validated_vehicles)
                        stats.successful_queries += 1
                        
                        self.logger.info(
                            f"✅ {query.manufacturer} {query.model}: "
                            f"{len(validated_vehicles)} validated vehicles"
                        )
                
                except Exception as e:
                    error_msg = f"{query.manufacturer} {query.model}: Exception - {str(e)}"
                    errors.append(error_msg)
                    stats.failed_queries += 1
                    self.logger.error(error_msg)
                
                # Rate limiting between requests
                time.sleep(self.delay_between_requests)
        
        # Remove duplicates based on listingId
        unique_vehicles = self._remove_duplicates(all_vehicles)
        
        # Calculate final stats
        stats.end_time = datetime.now()
        stats.total_vehicles = len(unique_vehicles)
        stats.total_cost_usd = (stats.total_vehicles / 1000) * self.cost_per_1000_results
        
        # Log summary
        self.logger.info(f"🎯 Collection complete:")
        self.logger.info(f"   Total vehicles: {stats.total_vehicles}")
        self.logger.info(f"   Successful queries: {stats.successful_queries}")
        self.logger.info(f"   Failed queries: {stats.failed_queries}")
        self.logger.info(f"   Duration: {stats.duration_minutes():.1f} minutes")
        self.logger.info(f"   Estimated cost: ${stats.total_cost_usd:.2f}")
        
        if errors:
            self.logger.warning(f"Errors encountered: {errors}")
        
        return unique_vehicles, stats
    
    def _remove_duplicates(self, vehicles: List[Dict]) -> List[Dict]:
        """Remove duplicate vehicles based on listingId"""
        seen_ids = set()
        unique_vehicles = []
        
        for vehicle in vehicles:
            listing_id = vehicle.get('listingId')
            if listing_id and listing_id not in seen_ids:
                seen_ids.add(listing_id)
                unique_vehicles.append(vehicle)
        
        return unique_vehicles
    
    def save_to_csv(self, vehicles: List[Dict], filename: str) -> str:
        """Save vehicle data to CSV file"""
        if not vehicles:
            raise ValueError("No vehicles to save")
        
        # Define CSV columns
        csv_columns = [
            'listingId', 'url', 'manufacturerEn', 'modelEn', 'subModel', 
            'year', 'km', 'hand', 'price', 'currency',
            'colorEn', 'engineVolume', 'horsePower', 'gearBox', 'engineType',
            'seats', 'doors', 'bodyType', 'cityEn', 'areaEn',
            'testDate', 'isAgent', 'updatedAt', 'data_quality_score'
        ]
        
        filepath = f"/home/omer/.openclaw/workspace/{filename}"
        
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns, extrasaction='ignore')
            writer.writeheader()
            
            for vehicle in vehicles:
                # Ensure all required fields exist
                row = {col: vehicle.get(col, '') for col in csv_columns}
                writer.writerow(row)
        
        self.logger.info(f"💾 Saved {len(vehicles)} vehicles to {filepath}")
        return filepath
    
    def generate_summary_report(self, vehicles: List[Dict], stats: CollectionStats) -> Dict:
        """Generate comprehensive summary report"""
        if not vehicles:
            return {"error": "No vehicles to analyze"}
        
        # Basic statistics
        prices = [v['price'] for v in vehicles if v.get('price', 0) > 0]
        years = [v['year'] for v in vehicles if v.get('year', 0) > 0]
        kms = [v['km'] for v in vehicles if v.get('km', 0) > 0]
        
        # Manufacturer/model breakdown
        manufacturer_counts = {}
        model_counts = {}
        
        for vehicle in vehicles:
            mfg = vehicle.get('manufacturerEn', 'Unknown')
            model = vehicle.get('modelEn', 'Unknown')
            
            manufacturer_counts[mfg] = manufacturer_counts.get(mfg, 0) + 1
            model_key = f"{mfg} {model}"
            model_counts[model_key] = model_counts.get(model_key, 0) + 1
        
        report = {
            "collection_stats": {
                "total_vehicles": stats.total_vehicles,
                "successful_queries": stats.successful_queries,
                "failed_queries": stats.failed_queries,
                "duration_minutes": round(stats.duration_minutes(), 2),
                "estimated_cost_usd": round(stats.total_cost_usd, 2)
            },
            "data_quality": {
                "average_quality_score": round(
                    sum(v.get('data_quality_score', 0) for v in vehicles) / len(vehicles), 3
                ),
                "high_quality_vehicles": sum(1 for v in vehicles if v.get('data_quality_score', 0) > 0.8),
                "complete_price_data": len(prices),
                "complete_mileage_data": len([v for v in vehicles if v.get('km', 0) > 0])
            },
            "market_analysis": {
                "price_range_ils": {
                    "min": min(prices) if prices else 0,
                    "max": max(prices) if prices else 0,
                    "average": round(sum(prices) / len(prices)) if prices else 0,
                    "median": sorted(prices)[len(prices)//2] if prices else 0
                },
                "year_range": {
                    "min": min(years) if years else 0,
                    "max": max(years) if years else 0
                },
                "mileage_range_km": {
                    "min": min(kms) if kms else 0,
                    "max": max(kms) if kms else 0,
                    "average": round(sum(kms) / len(kms)) if kms else 0
                }
            },
            "manufacturer_breakdown": dict(sorted(manufacturer_counts.items(), key=lambda x: x[1], reverse=True)),
            "model_breakdown": dict(sorted(model_counts.items(), key=lambda x: x[1], reverse=True)[:10])
        }
        
        return report

def main():
    """Example usage of CarValuationAPI"""
    print("🚗 **Car Valuation API - Production System**")
    print("="*50)
    
    # Check for API token
    api_token = os.getenv('APIFY_API_TOKEN')
    if not api_token:
        print("❌ Please set APIFY_API_TOKEN environment variable")
        return
    
    # Initialize API
    api = CarValuationAPI(api_token)
    
    # Example: Collect sample data
    sample_queries = [
        VehicleQuery("Toyota", "Corolla", 2018, 2020, "tel aviv", 20),
        VehicleQuery("Honda", "Civic", 2018, 2020, "tel aviv", 20),
    ]
    
    print("🔄 Starting sample data collection...")
    vehicles, stats = api.collect_all_vehicles(sample_queries)
    
    if vehicles:
        # Save data
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        csv_file = api.save_to_csv(vehicles, f"car_valuation_sample_{timestamp}.csv")
        
        # Generate report
        report = api.generate_summary_report(vehicles, stats)
        
        # Save report
        report_file = f"/home/omer/.openclaw/workspace/collection_report_{timestamp}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Sample collection complete!")
        print(f"📊 {stats.total_vehicles} vehicles collected")
        print(f"💰 Estimated cost: ${stats.total_cost_usd:.2f}")
        print(f"💾 Data saved to: {csv_file}")
        print(f"📋 Report saved to: {report_file}")
    
    else:
        print("❌ No vehicles collected")

if __name__ == "__main__":
    main()