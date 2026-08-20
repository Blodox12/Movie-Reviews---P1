from csv import DictReader
from datetime import datetime
from pathlib import Path

from django.core.management.base import BaseCommand
from django.utils import timezone

from news.models import News


class Command(BaseCommand):
	help = 'Load the first 5 news items from Fake.csv into the News model'

	def handle(self, *args, **kwargs):
		csv_file_path = Path(__file__).resolve().parent / 'Fake.csv'

		created_count = 0
		updated_count = 0

		try:
			with csv_file_path.open(mode='r', encoding='utf-8') as file:
				reader = DictReader(file)

				for index, news_item in enumerate(reader):
					if index == 5:
						break

					parsed_date = self.parse_date(news_item['date'])

					obj, created = News.objects.update_or_create(
						headline=news_item['title'].strip(),
						defaults={
							'body': news_item['text'].strip(),
							'date': parsed_date,
						},
					)

					if created:
						created_count += 1
					else:
						updated_count += 1

			self.stdout.write(
				self.style.SUCCESS(
					f'Import completed. Created: {created_count}, Updated: {updated_count}'
				)
			)

		except FileNotFoundError:
			self.stdout.write(
				self.style.ERROR(f'File not found: {csv_file_path}')
			)

		except Exception as e:
			self.stdout.write(
				self.style.ERROR(f'Unexpected error: {e}')
			)

	def parse_date(self, raw_date):
		raw_date = raw_date.strip()

		for date_format in ('%B %d, %Y', '%b %d, %Y', '%Y-%m-%d'):
			try:
				parsed_date = datetime.strptime(raw_date, date_format)
				return timezone.make_aware(parsed_date)
			except ValueError:
				continue

		raise ValueError(f'Unsupported date format: {raw_date}')
