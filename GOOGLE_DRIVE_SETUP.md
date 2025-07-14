# 🔧 วิธีการตั้งค่า Google Drive API สำหรับ Heckx AI Assistant

## 📋 ขั้นตอนที่ 1: สร้าง Google Cloud Project

1. **ไปที่ Google Cloud Console**
   - เปิด https://console.cloud.google.com
   - ล็อกอินด้วย Google Account

2. **สร้าง Project ใหม่**
   - คลิก dropdown "Select a project" ด้านบน
   - คลิก "NEW PROJECT"
   - ตั้งชื่อ project เช่น "Heckx-Music-Drive"
   - คลิก "CREATE"

## 📋 ขั้นตอนที่ 2: เปิดใช้งาน Google Drive API

1. **ไปที่ API Library**
   - ใน Google Cloud Console หา "APIs & Services" ในเมนูซ้าย
   - คลิก "Library"

2. **ค้นหาและเปิดใช้งาน API**
   - ค้นหา "Google Drive API"
   - คลิกเข้าไปที่ "Google Drive API"
   - คลิก "ENABLE"

## 📋 ขั้นตอนที่ 3: สร้าง Service Account (แนะนำ)

### วิธีที่ 1: Service Account Credentials (ปลอดภัยที่สุด)

1. **ไปที่ Credentials**
   - ใน "APIs & Services" เลือก "Credentials"
   - คลิก "+ CREATE CREDENTIALS"
   - เลือก "Service account"

2. **ตั้งค่า Service Account**
   - Service account name: `heckx-music-service`
   - Service account ID: จะสร้างอัตโนมัติ
   - Description: `Service account for music file management`
   - คลิก "CREATE AND CONTINUE"

3. **กำหนด Role**
   - เลือก Role: "Editor" หรือ "Storage Admin"
   - คลิก "CONTINUE"
   - คลิก "DONE"

4. **สร้าง JSON Key**
   - ในหน้า Credentials หา Service Account ที่สร้างใหม่
   - คลิกที่ service account email
   - ไปที่ tab "KEYS"
   - คลิก "ADD KEY" > "Create new key"
   - เลือก "JSON"
   - คลิก "CREATE"
   - ไฟล์ JSON จะ download อัตโนมัติ

## 📋 ขั้นตอนที่ 4: เพิ่ม Credentials ใน Railway

### สำหรับ Service Account (วิธีที่ 1):

1. **เปิดไฟล์ JSON ที่ download มา** จะมีหน้าตาประมาณนี้:
```json
{
  "type": "service_account",
  "project_id": "heckx-music-drive-123456",
  "private_key_id": "abcd1234...",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvAIBADANBgkqhkiG...\n-----END PRIVATE KEY-----\n",
  "client_email": "heckx-music-service@heckx-music-drive-123456.iam.gserviceaccount.com",
  "client_id": "123456789012345678901",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/..."
}
```

2. **Copy เนื้อหาทั้งหมดในไฟล์ JSON**

3. **ไปที่ Railway Dashboard**
   - เปิด https://railway.app
   - เข้าไปที่ project "Heckx AI Assistant"
   - คลิก tab "Variables"

4. **เพิ่ม Environment Variable**
   - คลิก "New Variable"
   - Name: `GOOGLE_DRIVE_CREDENTIALS`
   - Value: วางเนื้อหา JSON ทั้งหมด (ห่อด้วย single quotes ถ้าจำเป็น)
   - คลิก "Add"

### สำหรับ API Key (วิธีที่ 2 - ง่ายกว่าแต่จำกัดการใช้งาน):

1. **สร้าง API Key**
   - ใน Google Cloud Console ไปที่ "Credentials"
   - คลิก "+ CREATE CREDENTIALS"
   - เลือก "API key"
   - Copy API Key ที่ได้

2. **เพิ่มใน Railway**
   - Name: `GOOGLE_DRIVE_API_KEY`
   - Value: วาง API Key ที่ copy มา

## 📋 ขั้นตอนที่ 5: Deploy และทดสอบ

1. **Deploy ใหม่**
   - Railway จะ deploy อัตโนมัติเมื่อเพิ่ม environment variables
   - รอ 2-3 นาที

2. **ทดสอบการเชื่อมต่อ**
   - เปิดเว็บ Heckx AI Assistant
   - ไปที่ tab "🎵 Music"
   - คลิก "🔧 Test Drive"
   - ถ้าสำเร็จจะแสดง "✅ Google Drive Connection Test"

3. **ทดสอบการ Sync**
   - คลิก "☁️ Sync to Drive"
   - ควรแสดงสถานะ "Google Drive integration is active"

## 🔒 ความปลอดภัย

### สำหรับ Service Account:
- เก็บไฟล์ JSON ไว้ในที่ปลอดภัย
- อย่าแชร์ private_key กับผู้อื่น
- ลบไฟล์ JSON ในเครื่องหลังจาก copy ไปใช้แล้ว

### สำหรับ API Key:
- ตั้งค่า restrictions ใน Google Cloud Console
- จำกัด API ที่ใช้งานได้เฉพาะ Google Drive API
- จำกัด IP หรือ domain ถ้าเป็นไปได้

## ❓ Troubleshooting

### ถ้า Test Drive ล้มเหลว:
1. ตรวจสอบว่า environment variable ถูกต้อง
2. ตรวจสอบว่า Google Drive API เปิดใช้งานแล้ว
3. ตรวจสอบ JSON format ไม่เสียหาย
4. Deploy ใหม่อีกครั้ง

### ถ้าได้ Error "Permission denied":
1. ตรวจสอบ Role ของ Service Account
2. เพิ่ม Role "Storage Admin" หรือ "Editor"
3. รอ 10-15 นาทีให้ permissions มีผล

## 💡 Tips

1. **ใช้ Service Account** แทน API Key เพื่อความปลอดภัย
2. **สร้าง folder "Heckx Music Library"** ใน Google Drive เพื่อจัดระเบียบ
3. **ตั้งชื่อ project** ให้จำได้ง่าย
4. **เก็บ backup** ของ credentials ไว้ในที่ปลอดภัย

---
✅ **หลังจากทำตามขั้นตอนนี้แล้ว Google Drive integration จะพร้อมใช้งาน!**