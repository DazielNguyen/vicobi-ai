# Schemas Documentation

## 📚 Tổng quan

Folder schemas chứa các Pydantic models để validate và serialize dữ liệu cho API.

**Cấu trúc:**

- `base.py`: Base schemas cho transaction details, amounts
- `voice.py`: Voice schemas cho CRUD operations
- `bill.py`: Bill schemas cho CRUD operations
- `display.py`: Display schemas tối ưu cho frontend rendering

---

## 🎯 Schema Types

### 1. **Request Schemas** (từ Frontend → Backend)

- `VoiceCreateRequest`: Tạo Voice mới
- `VoiceUpdateRequest`: Update Voice
- `BillCreateRequest`: Tạo Bill mới
- `BillUpdateRequest`: Update Bill

### 2. **Response Schemas** (từ Backend → Frontend)

- `VoiceResponse`: Response Voice đơn lẻ
- `VoiceListResponse`: Response danh sách Voice
- `BillResponse`: Response Bill đơn lẻ
- `BillListResponse`: Response danh sách Bill

### 3. **Display Schemas** (tối ưu cho UI)

- `VoiceSummaryDisplay`: Tóm tắt Voice cho dashboard/list
- `VoiceDetailDisplay`: Chi tiết Voice cho trang detail
- `BillSummaryDisplay`: Tóm tắt Bill cho dashboard/list
- `BillDetailDisplay`: Chi tiết Bill cho trang detail (bảng hóa đơn)
- `DashboardStatsDisplay`: Thống kê tổng quan
- `TransactionChartData`: Data cho biểu đồ

---

## 📖 Usage Guide

### Voice API Examples

#### 1. Create Voice (POST /voices)

**Request:**

```json
{
  "voice_id": "voice_20251112_001",
  "total_amount": {
    "incomes": 5000000.0,
    "expenses": 3250000.0
  },
  "transactions": {
    "incomes": [
      {
        "transaction_type": "income",
        "description": "Lương tháng 11",
        "amount": 3000000.0,
        "amount_string": "3 triệu",
        "quantity": 1.0
      }
    ],
    "expenses": [
      {
        "transaction_type": "expense",
        "description": "Tiền thuê nhà",
        "amount": 2000000.0,
        "amount_string": "2 triệu",
        "quantity": 1.0
      }
    ]
  },
  "money_type": "VND"
}
```

**Response:**

```json
{
  "voice_id": "voice_20251112_001",
  "total_amount": {
    "incomes": 5000000.0,
    "expenses": 3250000.0
  },
  "transactions": {
    "incomes": [...],
    "expenses": [...]
  },
  "money_type": "VND",
  "utc_time": "2025-11-12T10:30:00.000Z"
}
```

#### 2. Get Voice Detail (GET /voices/{voice_id}/display)

**Response (Display format):**

```json
{
  "voice_id": "voice_20251112_001",
  "date": "2025-11-12T10:30:00.000Z",
  "money_type": "VND",
  "incomes": [
    {
      "stt": 1,
      "type": "income",
      "description": "Lương tháng 11",
      "amount": 3000000.0,
      "amount_formatted": "3 triệu",
      "quantity": 1.0,
      "subtotal": 3000000.0,
      "subtotal_formatted": "3 triệu"
    }
  ],
  "total_incomes": 5000000.0,
  "total_incomes_formatted": "5 triệu",
  "expenses": [
    {
      "stt": 1,
      "type": "expense",
      "description": "Tiền thuê nhà",
      "amount": 2000000.0,
      "amount_formatted": "2 triệu",
      "quantity": 1.0,
      "subtotal": 2000000.0,
      "subtotal_formatted": "2 triệu"
    }
  ],
  "total_expenses": 3250000.0,
  "total_expenses_formatted": "3,25 triệu",
  "balance": 1750000.0,
  "balance_formatted": "1,75 triệu"
}
```

### Bill API Examples

#### 3. Create Bill (POST /bills)

**Request:**

```json
{
  "bill_id": "bill_20251112_001",
  "total_amount": {
    "expenses": 23920000.0
  },
  "transactions": {
    "expenses": [
      {
        "transaction_type": "expense",
        "description": "Mua laptop",
        "amount": 25000000.0,
        "discount": 2500000.0,
        "amount_after_discount": 22500000.0,
        "amount_string_after_discount": "22,5 triệu",
        "quantity": 1.0
      }
    ]
  },
  "money_type": "VND"
}
```

#### 4. Get Bill Detail (GET /bills/{bill_id}/display)

**Response (Display format - Table format):**

```json
{
  "bill_id": "bill_20251112_002",
  "date": "2025-11-12T20:15:00.000Z",
  "money_type": "VND",
  "items": [
    {
      "stt": 1,
      "name": "Mua laptop",
      "quantity": 1.0,
      "price": 25000000.0,
      "price_formatted": "25 triệu",
      "discount": 2500000.0,
      "discount_formatted": "2,5 triệu",
      "price_after_discount": 22500000.0,
      "price_after_discount_formatted": "22,5 triệu",
      "subtotal": 22500000.0,
      "subtotal_formatted": "22,5 triệu"
    },
    {
      "stt": 2,
      "name": "Mua chuột không dây",
      "quantity": 1.0,
      "price": 450000.0,
      "price_formatted": "450 nghìn",
      "discount": 50000.0,
      "discount_formatted": "50 nghìn",
      "price_after_discount": 400000.0,
      "price_after_discount_formatted": "400 nghìn",
      "subtotal": 400000.0,
      "subtotal_formatted": "400 nghìn"
    }
  ],
  "total_before_discount": 25450000.0,
  "total_before_discount_formatted": "25,45 triệu",
  "total_discount": 2550000.0,
  "total_discount_formatted": "2,55 triệu",
  "total_amount": 22900000.0,
  "total_amount_formatted": "22,9 triệu"
}
```

---

## 🔑 Key Features

### 1. **Validation tự động**

- Pydantic validate tất cả fields
- `amount_after_discount` = `amount` - `discount` được check tự động
- Tất cả amount phải >= 0

### 2. **Formatted strings sẵn có**

- `amount_formatted`: "3 triệu", "500 nghìn"
- `subtotal_formatted`: Tính sẵn amount × quantity
- Frontend không cần format, chỉ hiển thị

### 3. **STT (Số thứ tự) tự động**

- Display schemas có field `stt` để render table dễ dàng
- Backend tự động đánh số

### 4. **Tính toán sẵn**

- `subtotal`: amount × quantity
- `balance`: incomes - expenses
- `total_discount`: Tổng giảm giá

### 5. **Optimized cho frontend**

- Display schemas có đầy đủ data cần thiết
- Giảm logic xử lý ở frontend
- Giảm số lần gọi API

---

## 📝 Lưu ý quan trọng

### 1. **2 loại schemas:**

**Standard schemas** (voice.py, bill.py):

- Dùng cho CRUD operations
- Match với MongoDB structure
- Validation cơ bản

**Display schemas** (display.py):

- Dùng cho frontend rendering
- Có thêm computed fields
- Formatted strings sẵn
- STT, subtotals đã tính

### 2. **Khi nào dùng schema nào:**

**Create/Update**: Dùng `*CreateRequest`, `*UpdateRequest`

```
POST /voices → VoiceCreateRequest
PUT /voices/{id} → VoiceUpdateRequest
```

**Get single item**: Dùng `*Response` hoặc `*DetailDisplay`

```
GET /voices/{id} → VoiceResponse (raw data)
GET /voices/{id}/display → VoiceDetailDisplay (formatted for UI)
```

**Get list**: Dùng `*ListResponse` hoặc `*SummaryDisplay`

```
GET /voices → VoiceListResponse
GET /voices/summary → List[VoiceSummaryDisplay]
```
