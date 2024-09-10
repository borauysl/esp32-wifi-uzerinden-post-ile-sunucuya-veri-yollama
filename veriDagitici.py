import mysql.connector
import requests
import time

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="1234",
        database="rafetiket"
    )

def get_latest_data(cursor):
    query = "SELECT urunBarkod, urunIsim, urunFiyat, etiketIP FROM etiket"
    cursor.execute(query)
    return cursor.fetchall()

def update_etiket_aktif(cursor, etiketIP, status):
    query = "UPDATE etiket SET etiketAktif = %s WHERE etiketIP = %s"
    cursor.execute(query, (status, etiketIP))

def update_urun_indirimli(db , cursor, urunBarkod, urunFiyat, urunIndirimMiktar):
    if urunIndirimMiktar is not None and urunIndirimMiktar != 0:
        urunIndirimli = urunFiyat - urunIndirimMiktar
        query = "UPDATE etiket SET urunIndirimli = %s WHERE urunBarkod = %s"
        cursor.execute(query, (urunIndirimli, urunBarkod))
    else:
        # indirim yoksa bosalt
        query = "UPDATE etiket SET urunIndirimli = NULL WHERE urunBarkod = %s"
        cursor.execute(query, (urunBarkod,))
    db.commit()
def main():
    while True:
        db = get_db_connection()
        cursor = db.cursor()

        # Veriyi SQL'den çekme
        rows = get_latest_data(cursor)

        # Her kayıt için IP adresine veri yollama
        for row in rows:
            urunBarkod, urunIsim, urunFiyat, etiketIP = row

            # IP adresinin kontrolü
            if not etiketIP or etiketIP.lower() == 'null':
                update_etiket_aktif(cursor, etiketIP, "pasif")  # etiketAktif 'pasif' olarak güncelleniyor
                db.commit()  # Veritabanına güncellemeyi uygula
                print(f"IP ADRESİ BULUNDU: {etiketIP}")
                continue
            else:
                print(f"Veritabanından elde edilen IP Adresi: {etiketIP}")

            # Ürün indirimi kontrolü
            cursor.execute("SELECT urunIndirimMiktar FROM etiket WHERE urunBarkod = %s", (urunBarkod,))
            urunIndirimMiktar = cursor.fetchone()[0]

            # İndirimli fiyatı güncelle
            update_urun_indirimli(db, cursor, urunBarkod, urunFiyat, urunIndirimMiktar)

            # ESP32'ye veri gönderme
            if urunIndirimMiktar is not None and urunIndirimMiktar != 0:
                # İndirim varsa indirimi ve indirimli fiyatı da gönder
                cursor.execute("SELECT urunIndirimli FROM etiket WHERE urunBarkod = %s", (urunBarkod,))
                urunIndirimli = cursor.fetchone()[0]
                data = {
                    "urunBarkod": urunBarkod,
                    "urunIsim": urunIsim,
                    "urunFiyat": str(urunFiyat),
                    "urunIndirimMiktar": str(urunIndirimMiktar),
                    "urunIndirimli": str(urunIndirimli)
                }
            else:
                # İndirim yoksa sadece barkod, isim ve fiyat gönder
                data = {
                    "urunBarkod": urunBarkod,
                    "urunIsim": urunIsim,
                    "urunFiyat": str(urunFiyat)
                }

            # IP adresine POST gönderme
            url = f"http://{etiketIP}/update"
            try:
                response = requests.post(url, json=data, headers={"Content-Type": "application/json"})
                print(f"Yanıt Kodu: {response.status_code}")  # ESP32'den gelen yanıt kodu

                if response.status_code == 200:
                    print(f"Veri {etiketIP} adresine başarıyla gönderildi.")
                    update_etiket_aktif(cursor, etiketIP, "aktif")  # etiketAktif 'aktif' olarak güncelleniyor
                else:
                    print(f"Veri gönderiminde hata: {response.status_code}, Yanıt: {response.text}")
                    update_etiket_aktif(cursor, etiketIP, "pasif")  # Yanıt kodu 200 değilse 'pasif' olarak güncelleniyor

                db.commit()  # Veritabanına güncellemeyi uygula
            except requests.exceptions.RequestException as e:
                print(f"Bağlantı hatası: {e}")
                update_etiket_aktif(cursor, etiketIP, "pasif")  # Bağlantı hatası durumunda 'pasif' olarak güncelleniyor
                db.commit()  # Veritabanına güncellemeyi uygula

        cursor.close()
        db.close()

        time.sleep(5)  # 5 saniyede bir döngü tekrar ediyor

if __name__ == "__main__":
    main()