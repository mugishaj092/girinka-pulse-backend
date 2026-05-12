"""
Django management command to test weather data fetching
"""
from django.core.management.base import BaseCommand
from features.weather.tasks import fetch_daily_weather
from features.weather.models import WeatherData
from features.districts.models import District


class Command(BaseCommand):
    help = 'Test weather API integration and fetch real data'

    def handle(self, *args, **options):
        self.stdout.write("=" * 70)
        self.stdout.write(self.style.SUCCESS("TESTING WEATHER API INTEGRATION"))
        self.stdout.write("=" * 70)
        
        # Check districts
        districts_count = District.objects.count()
        self.stdout.write(f"\nDistricts in database: {districts_count}")
        
        if districts_count == 0:
            self.stdout.write(self.style.ERROR("No districts found! Run seed_all command first."))
            return
        
        # Show sample district
        sample = District.objects.first()
        self.stdout.write(f"Sample district: {sample.district_name} ({sample.latitude}, {sample.longitude})")
        
        # Check existing weather data
        existing_count = WeatherData.objects.count()
        self.stdout.write(f"Existing weather records: {existing_count}")
        
        # Run the fetch task
        self.stdout.write("\n" + "-" * 70)
        self.stdout.write("Running fetch_daily_weather task...")
        self.stdout.write("-" * 70)
        
        try:
            records_created = fetch_daily_weather()
            self.stdout.write(self.style.SUCCESS(f"\n[OK] Task completed! Created/updated {records_created} records"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"\n[ERROR] Task failed: {e}"))
            import traceback
            traceback.print_exc()
            return
        
        # Show results
        new_count = WeatherData.objects.count()
        self.stdout.write(f"\nTotal weather records now: {new_count}")
        
        # Display sample data
        self.stdout.write("\n" + "-" * 70)
        self.stdout.write("SAMPLE WEATHER DATA (Latest 5 records):")
        self.stdout.write("-" * 70)
        
        latest = WeatherData.objects.select_related('district').order_by('-reading_time')[:5]
        for record in latest:
            self.stdout.write(
                f"{record.district.district_name:15} | "
                f"{record.reading_time.strftime('%Y-%m-%d')} | "
                f"Temp: {record.temperature}C | "
                f"Rain: {record.rainfall}mm | "
                f"Humidity: {record.humidity}%"
            )
        
        self.stdout.write("\n" + "=" * 70)
        self.stdout.write(self.style.SUCCESS("[SUCCESS] Weather API is working correctly!"))
        self.stdout.write("=" * 70)
