import requests
import logging
import re
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from io import BytesIO
import math
import sys

class MTGProxyGenerator:
    def __init__(self, scale_factor=0.95, margin = 0.5):
        self.CARD_WIDTH = 2.5 * 72  # 2.5 inches in points
        self.CARD_HEIGHT = 3.5 * 72  # 3.5 inches in points
        self.SCALE_FACTOR = scale_factor # 5% reduction
        self.PAGE_WIDTH = 8.5 * 72  # 8.5 inches in points
        self.PAGE_HEIGHT = 11 * 72  # 11 inches in points
        self.MARGIN = margin * 72  # 0.25 inch margin

    def parse_decklist(self, decklist_text):
        """Parse common decklist formats (Arena, Manabox, etc.)"""
        cards = []
        for line in decklist_text.split('\n'):
            if not line.strip():
                continue
            
            # Match patterns like "4 Lightning Bolt" or "4x Lightning Bolt"
            match = re.match(r'^(\d+)x?\s+(.+)$', line.strip())
            if match:
                count = int(match.group(1))
                card_name = match.group(2)
                # strip out trailing set info from, e.g., manabox output
                match = re.match(r'^(.*)\s+(\([A-Z0-9]*\)\s+[0-9]*)$', card_name)
                if match:
                    card_name = match.group(1)
                    if True:
                        print(f'stripped out {match.group(2)}');
                cards.extend([card_name] * count)
        
        return cards

    def get_card_image_urls(self, card_name):
        """Fetch card image URL from Scryfall API"""
        url = f"https://api.scryfall.com/cards/named?fuzzy={card_name}"
        logging.info(f"fetching card image {card_name}")
        response = requests.get(url)
        if response.status_code == 200:
            card_data = response.json()
            normal_image = card_data.get('image_uris', {}).get('border_crop')
            if normal_image is not None:
                return [normal_image]
            if card_data.get('card_faces') is not None:
                return [x.get('image_uris', {}).get('border_crop') for x in card_data['card_faces']]
        return None

    def create_proxy_pdf(self, decklist, output_filename):
        """Create PDF with proxy cards"""
        # Calculate scaled dimensions
        scaled_width = self.CARD_WIDTH * self.SCALE_FACTOR
        scaled_height = self.CARD_HEIGHT * self.SCALE_FACTOR

        # Calculate cards per row and column
        cards_per_row = math.floor((self.PAGE_WIDTH - 2 * self.MARGIN) / scaled_width)
        cards_per_column = math.floor((self.PAGE_HEIGHT - 2 * self.MARGIN) / scaled_height)

        # Create PDF
        c = canvas.Canvas(output_filename, pagesize=(self.PAGE_WIDTH, self.PAGE_HEIGHT))

        current_row = 0
        current_col = 0
        current_page = 1

        cards = self.parse_decklist(decklist)
        
        for card_name in cards:
            # Get image URL from Scryfall
            image_urls = self.get_card_image_urls(card_name)
            if len(image_urls) == 0:
                print(f"Could not find image for {card_name}")
                continue

            for image_url in image_urls:
                # Download and process image
                response = requests.get(image_url)
                img = Image.open(BytesIO(response.content))
                
                # Calculate position
                x = self.MARGIN + (current_col * scaled_width)
                y = self.PAGE_HEIGHT - self.MARGIN - ((current_row + 1) * scaled_height)

                # Add image to PDF
                c.drawImage(ImageReader(img), x, y, width=scaled_width, height=scaled_height)

                # Update position
                current_col += 1
                if current_col >= cards_per_row:
                    current_col = 0
                    current_row += 1

                # Check if we need a new page
                if current_row >= cards_per_column:
                    c.showPage()
                    current_page += 1
                    current_row = 0
                    current_col = 0

        c.save()

# Example usage
generator = MTGProxyGenerator()

# Example decklist
decklist = """
1 search for azcanta // azcanta, the sunken ruin
"""

if len(sys.argv) > 1:
    with open(sys.argv[1], 'r') as f:
        decklist = f.read()

generator.create_proxy_pdf(decklist, "proxies.pdf")
