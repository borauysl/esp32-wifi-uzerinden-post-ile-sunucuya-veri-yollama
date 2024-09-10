Geliştirdiğim ara program bir MySQL veritabanında bulunan ürün bilgilerini alarak bu bilgileri bir esp32 cihazına post isteği ile gönderir. Program her ürün için barkod, isim, fiyat, indirim miktarı gibi verileri alır ve esp32 ye iletir. Veritabanından alınan her kayıt, ip adresine sahip bir esp32 ile ilişkilendirilmiştir. Eğer ürün için indirim tanımlanmışsa, indirimli fiyat hesaplanarak gönderilir, aksi takdirde sadece standart ürün bilgileri gönderilir.

Veritabanında etiketin ip bilgisi yoksa veya geçersizse, o etiketin "aktif" durumu "pasif" olarak güncellenir. Eğer post isteği başarıyla gerçekleşirse, etiket "aktif" olarak işaretlenir, aksi durumda "pasif" olarak güncellenir. Program bu işlemi belirtilen sürede bir tekrar eder, böylece sürekli olarak ürün bilgilerinin güncel kalması sağlanır.

ESP32 cihazlarına veri gönderimi sırasında JSON formatı kullanılır ve içerik uygun şekilde yapılandırılarak her ip adresine gönderilir. Yanıt durumuna göre veritabanı güncellemeleri yapılır ve hatalar loglanır. elektronik etiket sistemleri için uygun bir çözüm olarak çalışır.

sql tablosu :
CREATE TABLE `etiket` (
  `etiketID` int NOT NULL AUTO_INCREMENT,
  `urunBarkod` varchar(45) DEFAULT NULL,
  `urunIsim` varchar(45) DEFAULT NULL,
  `urunFiyat` decimal(18,2) DEFAULT NULL,
  `etiketIP` varchar(45) NOT NULL,
  `etiketAktif` varchar(45) DEFAULT NULL,
  `urunIndirimMiktar` decimal(18,2) DEFAULT NULL,
  `urunIndirimli` decimal(18,2) DEFAULT NULL,
  PRIMARY KEY (`etiketID`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
