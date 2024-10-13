from flask import Flask, request, jsonify
from flasgger import Swagger
import requests

app = Flask(__name__)
swagger = Swagger(app)

# Barkod numarası kullanarak ürün bilgilerini ve fotoğrafları almak için fonksiyon
def get_full_barcode_info(barcode):
    url = f"https://api.upcitemdb.com/prod/trial/lookup?upc={barcode}"
    
    try:
        # API'ye GET isteği gönderiyoruz
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Hata kontrolü

        data = response.json()

        # Eğer ürün bulunamazsa bir hata mesajı döneriz
        if data['total'] == 0:
            return {"error": "No product information found for this barcode"}

        item = data['items'][0]

        # Tüm ilgili ürün bilgilerini ve fotoğrafları alıyoruz
        result = {
            "barcode": barcode,
            "product_name": item.get('title', 'Not found'),
            "brand": item.get('brand', 'Not found'),
            "category": item.get('category', 'Not found'),
            "description": item.get('description', 'Not found'),
            "lowest_recorded_price": item.get('lowest_recorded_price', 'Not found'),  # En düşük fiyat
            "highest_recorded_price": item.get('highest_recorded_price', 'Not found'),  # En yüksek fiyat
            "images": item.get('images', []),  # Ürüne ait resimler
            "offers": item.get('offers', [])  # Fiyat teklifleri ve satıcı bilgileri
        }

        return result
    
    except requests.RequestException as e:
        return {"error": f"Request failed: {str(e)}"}
    except Exception as e:
        return {"error": f"An unexpected error occurred: {str(e)}"}

# '/full_lookup/<barcode>' endpoint'i ürün bilgilerini alır
@app.route('/full_lookup/<barcode>', methods=['GET'])
def full_lookup_barcode(barcode):
    """
    Get product information by barcode.
    ---
    parameters:
      - name: barcode
        in: path
        type: string
        required: true
        description: The barcode of the product to look up.
    responses:
      200:
        description: A product information object
        schema:
          type: object
          properties:
            barcode:
              type: string
            product_name:
              type: string
            brand:
              type: string
            category:
              type: string
            description:
              type: string
            lowest_recorded_price:
              type: string
            highest_recorded_price:
              type: string
            images:
              type: array
              items:
                type: string
            offers:
              type: array
              items:
                type: object
      404:
        description: Product not found
    """
    result = get_full_barcode_info(barcode)
    return jsonify(result)

# Flask uygulamasını başlatıyoruz
if __name__ == '__main__':
    app.run(debug=True)