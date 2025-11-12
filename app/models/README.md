# Models Documentation

## 📚 Tổng quan

File này chứa các mẫu JSON và notes cho các Document trong MongoDB sử dụng MongoEngine.

**Các models:**

- **Voice**: Giao dịch thu chi từ giọng nói (có cả income và expense)
- **Bill**: Hóa đơn chi tiêu (chỉ có expense, có discount)

---

## 🎤 Voice Document

**Collection:** `Voices`  
**File:** `voice.py`

**Mô tả:** Lưu trữ thông tin giao dịch thu chi từ giọng nói, bao gồm cả thu nhập (incomes) và chi tiêu (expenses).

### Schema Fields

| Field          | Type                  | Required | Description                                |
| -------------- | --------------------- | -------- | ------------------------------------------ |
| `voice_id`     | String                | ✅       | ID duy nhất cho voice record               |
| `total_amount` | VoiceTotalAmountField | ✅       | Tổng số tiền thu/chi                       |
| `transactions` | VoiceTransactionField | ❌       | Chi tiết các giao dịch                     |
| `money_type`   | String                | ✅       | Loại tiền tệ (VND/USD/EUR) - Mặc định: VND |
| `utc_time`     | DateTime              | ❌       | Thời gian tạo (UTC) - Tự động              |

### VoiceTransactionDetailsField

| Field              | Type   | Required | Description                     |
| ------------------ | ------ | -------- | ------------------------------- |
| `transaction_type` | String | ✅       | Loại giao dịch (income/expense) |
| `description`      | String | ✅       | Mô tả giao dịch                 |
| `amount`           | Float  | ✅       | Số tiền (>= 0)                  |
| `amount_string`    | String | ✅       | Số tiền dạng chuỗi (format VND) |
| `quantity`         | Float  | ✅       | Số lượng (>= 0, mặc định = 1)   |

### VoiceTotalAmountField

| Field      | Type  | Required | Description                        |
| ---------- | ----- | -------- | ---------------------------------- |
| `incomes`  | Float | ✅       | Tổng thu nhập (>= 0, mặc định = 0) |
| `expenses` | Float | ✅       | Tổng chi tiêu (>= 0, mặc định = 0) |

### JSON Mẫu 1: Giao dịch cơ bản (VND)

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
      },
      {
        "transaction_type": "income",
        "description": "Thưởng dự án",
        "amount": 2000000.0,
        "amount_string": "2 triệu",
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
      },
      {
        "transaction_type": "expense",
        "description": "Tiền điện nước",
        "amount": 500000.0,
        "amount_string": "500 nghìn",
        "quantity": 1.0
      },
      {
        "transaction_type": "expense",
        "description": "Mua sắm",
        "amount": 750000.0,
        "amount_string": "750 nghìn",
        "quantity": 1.0
      }
    ]
  },
  "money_type": "VND",
  "utc_time": "2025-11-12T10:30:00.000Z"
}
```

### JSON Mẫu 2: Giao dịch với số lượng (quantity > 1)

```json
{
  "voice_id": "voice_20251112_002",
  "total_amount": {
    "incomes": 0.0,
    "expenses": 1250000.0
  },
  "transactions": {
    "incomes": [],
    "expenses": [
      {
        "transaction_type": "expense",
        "description": "Mua áo thun",
        "amount": 150000.0,
        "amount_string": "150 nghìn",
        "quantity": 3.0
      },
      {
        "transaction_type": "expense",
        "description": "Mua sách",
        "amount": 85000.0,
        "amount_string": "85 nghìn",
        "quantity": 5.0
      },
      {
        "transaction_type": "expense",
        "description": "Cà phê",
        "amount": 45000.0,
        "amount_string": "45 nghìn",
        "quantity": 2.0
      }
    ]
  },
  "money_type": "VND",
  "utc_time": "2025-11-12T14:20:00.000Z"
}
```

### JSON Mẫu 3: Thu nhập lớn

```json
{
  "voice_id": "voice_20251112_003",
  "total_amount": {
    "incomes": 125500000.0,
    "expenses": 0.0
  },
  "transactions": {
    "incomes": [
      {
        "transaction_type": "income",
        "description": "Lương + thưởng cuối năm",
        "amount": 25000000.0,
        "amount_string": "25 triệu",
        "quantity": 1.0
      },
      {
        "transaction_type": "income",
        "description": "Dự án freelance",
        "amount": 15500000.0,
        "amount_string": "15,5 triệu",
        "quantity": 1.0
      },
      {
        "transaction_type": "income",
        "description": "Thu nhập từ đầu tư",
        "amount": 85000000.0,
        "amount_string": "85 triệu",
        "quantity": 1.0
      }
    ],
    "expenses": []
  },
  "money_type": "VND",
  "utc_time": "2025-11-12T16:45:00.000Z"
}
```

---

## 🧾 Bill Document

**Collection:** `Bills`  
**File:** `bill.py`

**Mô tả:** Lưu trữ thông tin hóa đơn chi tiêu, chỉ bao gồm các khoản chi (expenses) với hỗ trợ discount.

### Schema Fields

| Field          | Type                 | Required | Description                                |
| -------------- | -------------------- | -------- | ------------------------------------------ |
| `bill_id`      | String               | ✅       | ID duy nhất cho bill record                |
| `total_amount` | BillTotalAmountField | ✅       | Tổng số tiền chi (sau discount)            |
| `transactions` | BillTransactionField | ❌       | Chi tiết các giao dịch                     |
| `money_type`   | String               | ✅       | Loại tiền tệ (VND/USD/EUR) - Mặc định: VND |
| `utc_time`     | DateTime             | ❌       | Thời gian tạo (UTC) - Tự động              |

### BillTransactionDetailsField

| Field                          | Type   | Required | Description                           |
| ------------------------------ | ------ | -------- | ------------------------------------- |
| `transaction_type`             | String | ✅       | Loại giao dịch (expense)              |
| `description`                  | String | ✅       | Mô tả giao dịch                       |
| `amount`                       | Float  | ✅       | Số tiền gốc (>= 0)                    |
| `discount`                     | Float  | ❌       | Số tiền giảm giá (>= 0, mặc định = 0) |
| `amount_after_discount`        | Float  | ✅       | Số tiền sau giảm giá (>= 0)           |
| `amount_string_after_discount` | String | ✅       | Số tiền sau giảm giá dạng chuỗi       |
| `quantity`                     | Float  | ✅       | Số lượng (>= 0, mặc định = 1)         |

### BillTotalAmountField

| Field      | Type  | Required | Description                                       |
| ---------- | ----- | -------- | ------------------------------------------------- |
| `expenses` | Float | ✅       | Tổng chi tiêu (sau discount) (>= 0, mặc định = 0) |

### JSON Mẫu 1: Hóa đơn không có discount

```json
{
  "bill_id": "bill_20251112_001",
  "total_amount": {
    "expenses": 2750000.0
  },
  "transactions": {
    "expenses": [
      {
        "transaction_type": "expense",
        "description": "Hóa đơn điện",
        "amount": 850000.0,
        "discount": 0.0,
        "amount_after_discount": 850000.0,
        "amount_string_after_discount": "850 nghìn",
        "quantity": 1.0
      },
      {
        "transaction_type": "expense",
        "description": "Hóa đơn nước",
        "amount": 250000.0,
        "discount": 0.0,
        "amount_after_discount": 250000.0,
        "amount_string_after_discount": "250 nghìn",
        "quantity": 1.0
      },
      {
        "transaction_type": "expense",
        "description": "Hóa đơn internet",
        "amount": 350000.0,
        "discount": 0.0,
        "amount_after_discount": 350000.0,
        "amount_string_after_discount": "350 nghìn",
        "quantity": 1.0
      },
      {
        "transaction_type": "expense",
        "description": "Hóa đơn gas",
        "amount": 1300000.0,
        "discount": 0.0,
        "amount_after_discount": 1300000.0,
        "amount_string_after_discount": "1,3 triệu",
        "quantity": 1.0
      }
    ]
  },
  "money_type": "VND",
  "utc_time": "2025-11-12T15:45:00.000Z"
}
```

### JSON Mẫu 2: Hóa đơn có discount

```json
{
  "bill_id": "bill_20251112_002",
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
      },
      {
        "transaction_type": "expense",
        "description": "Mua chuột không dây",
        "amount": 450000.0,
        "discount": 50000.0,
        "amount_after_discount": 400000.0,
        "amount_string_after_discount": "400 nghìn",
        "quantity": 1.0
      },
      {
        "transaction_type": "expense",
        "description": "Bàn phím cơ",
        "amount": 1200000.0,
        "discount": 180000.0,
        "amount_after_discount": 1020000.0,
        "amount_string_after_discount": "1,02 triệu",
        "quantity": 1.0
      }
    ]
  },
  "money_type": "VND",
  "utc_time": "2025-11-12T20:15:00.000Z"
}
```

### JSON Mẫu 3: Hóa đơn mua sắm với nhiều sản phẩm

```json
{
  "bill_id": "bill_20251112_003",
  "total_amount": {
    "expenses": 2835000.0
  },
  "transactions": {
    "expenses": [
      {
        "transaction_type": "expense",
        "description": "Áo thun",
        "amount": 250000.0,
        "discount": 25000.0,
        "amount_after_discount": 225000.0,
        "amount_string_after_discount": "225 nghìn",
        "quantity": 3.0
      },
      {
        "transaction_type": "expense",
        "description": "Quần jeans",
        "amount": 600000.0,
        "discount": 120000.0,
        "amount_after_discount": 480000.0,
        "amount_string_after_discount": "480 nghìn",
        "quantity": 2.0
      },
      {
        "transaction_type": "expense",
        "description": "Giày sneaker",
        "amount": 1500000.0,
        "discount": 300000.0,
        "amount_after_discount": 1200000.0,
        "amount_string_after_discount": "1,2 triệu",
        "quantity": 1.0
      }
    ]
  },
  "money_type": "VND",
  "utc_time": "2025-11-12T18:30:00.000Z"
}
```

### JSON Mẫu 4: Hóa đơn siêu thị

```json
{
  "bill_id": "bill_20251112_004",
  "total_amount": {
    "expenses": 1156000.0
  },
  "transactions": {
    "expenses": [
      {
        "transaction_type": "expense",
        "description": "Gạo ST25",
        "amount": 180000.0,
        "discount": 0.0,
        "amount_after_discount": 180000.0,
        "amount_string_after_discount": "180 nghìn",
        "quantity": 2.0
      },
      {
        "transaction_type": "expense",
        "description": "Thịt bò",
        "amount": 420000.0,
        "discount": 20000.0,
        "amount_after_discount": 400000.0,
        "amount_string_after_discount": "400 nghìn",
        "quantity": 1.0
      },
      {
        "transaction_type": "expense",
        "description": "Rau củ quả",
        "amount": 156000.0,
        "discount": 0.0,
        "amount_after_discount": 156000.0,
        "amount_string_after_discount": "156 nghìn",
        "quantity": 1.0
      },
      {
        "transaction_type": "expense",
        "description": "Sữa tươi",
        "amount": 45000.0,
        "discount": 5000.0,
        "amount_after_discount": 40000.0,
        "amount_string_after_discount": "40 nghìn",
        "quantity": 6.0
      }
    ]
  },
  "money_type": "VND",
  "utc_time": "2025-11-12T09:30:00.000Z"
}
```

---

## 📋 Bill Display Format - Dạng Bảng Hóa Đơn

### Mẫu Bill 1: Hóa đơn tiện ích

**Bill ID:** `bill_20251112_001`  
**Ngày:** 2025-11-12  
**Loại tiền:** VND

| STT | Tên              | Số Lượng |         Giá |  Thành tiền |
| :-: | ---------------- | :------: | ----------: | ----------: |
|  1  | Hóa đơn điện     |    1     |   850.000 ₫ |   850.000 ₫ |
|  2  | Hóa đơn nước     |    1     |   250.000 ₫ |   250.000 ₫ |
|  3  | Hóa đơn internet |    1     |   350.000 ₫ |   350.000 ₫ |
|  4  | Hóa đơn gas      |    1     | 1.300.000 ₫ | 1.300.000 ₫ |

**Tổng cộng:** 2.750.000 ₫

---

### Mẫu Bill 2: Hóa đơn có giảm giá

**Bill ID:** `bill_20251112_002`  
**Ngày:** 2025-11-12  
**Loại tiền:** VND

| STT | Tên                 | Số Lượng |      Giá gốc |    Giảm giá | Giá sau giảm |   Thành tiền |
| :-: | ------------------- | :------: | -----------: | ----------: | -----------: | -----------: |
|  1  | Mua laptop          |    1     | 25.000.000 ₫ | 2.500.000 ₫ | 22.500.000 ₫ | 22.500.000 ₫ |
|  2  | Mua chuột không dây |    1     |    450.000 ₫ |    50.000 ₫ |    400.000 ₫ |    400.000 ₫ |
|  3  | Bàn phím cơ         |    1     |  1.200.000 ₫ |   180.000 ₫ |  1.020.000 ₫ |  1.020.000 ₫ |

**Tổng giảm giá:** 2.730.000 ₫  
**Tổng thanh toán:** 23.920.000 ₫

---

### Mẫu Bill 3: Hóa đơn mua sắm nhiều sản phẩm

**Bill ID:** `bill_20251112_003`  
**Ngày:** 2025-11-12  
**Loại tiền:** VND

| STT | Tên          | Số Lượng |     Giá gốc |  Giảm giá | Giá sau giảm |  Thành tiền |
| :-: | ------------ | :------: | ----------: | --------: | -----------: | ----------: |
|  1  | Áo thun      |    3     |   250.000 ₫ |  25.000 ₫ |    225.000 ₫ |   675.000 ₫ |
|  2  | Quần jeans   |    2     |   600.000 ₫ | 120.000 ₫ |    480.000 ₫ |   960.000 ₫ |
|  3  | Giày sneaker |    1     | 1.500.000 ₫ | 300.000 ₫ |  1.200.000 ₫ | 1.200.000 ₫ |

**Tổng giảm giá:** 445.000 ₫  
**Tổng thanh toán:** 2.835.000 ₫

---

### Mẫu Bill 4: Hóa đơn siêu thị

**Bill ID:** `bill_20251112_004`  
**Ngày:** 2025-11-12  
**Loại tiền:** VND

| STT | Tên        | Số Lượng |   Giá gốc | Giảm giá | Giá sau giảm | Thành tiền |
| :-: | ---------- | :------: | --------: | -------: | -----------: | ---------: |
|  1  | Gạo ST25   |    2     | 180.000 ₫ |      0 ₫ |    180.000 ₫ |  360.000 ₫ |
|  2  | Thịt bò    |    1     | 420.000 ₫ | 20.000 ₫ |    400.000 ₫ |  400.000 ₫ |
|  3  | Rau củ quả |    1     | 156.000 ₫ |      0 ₫ |    156.000 ₫ |  156.000 ₫ |
|  4  | Sữa tươi   |    6     |  45.000 ₫ |  5.000 ₫ |     40.000 ₫ |  240.000 ₫ |

**Tổng giảm giá:** 25.000 ₫  
**Tổng thanh toán:** 1.156.000 ₫

---

## 💱 Enum Values

### Transaction Type (`EnumTransactionTypeField`)

- `income` - Thu nhập
- `expense` - Chi tiêu

### Money Type (`EnumMoneyTypeField`)

- `VND` - Việt Nam Đồng (mặc định)
- `USD` - US Dollar
- `EUR` - Euro

---

## 📝 Notes & Lưu ý quan trọng

### 1. Sự khác biệt giữa Voice và Bill

| Feature  | Voice                         | Bill                        |
| -------- | ----------------------------- | --------------------------- |
| Incomes  | ✅ Có                         | ❌ Không                    |
| Expenses | ✅ Có                         | ✅ Có                       |
| Discount | ❌ Không                      | ✅ Có                       |
| Use Case | Ghi nhận thu chi từ giọng nói | Hóa đơn mua sắm có discount |

### 2. Field Descriptions

**Voice Model:**

- `amount`: Số tiền giao dịch (thu hoặc chi)
- `amount_string`: Số tiền format dạng "3 triệu", "500 nghìn" (dùng hàm `format_vnd_general()`)
- `quantity`: Số lượng (mặc định = 1, dùng khi mua nhiều items cùng loại)

**Bill Model:**

- `amount`: Số tiền gốc trước giảm giá
- `discount`: Số tiền được giảm (0 nếu không có discount)
- `amount_after_discount`: Số tiền sau khi trừ discount = `amount - discount`
- `amount_string_after_discount`: Số tiền sau discount format dạng "22,5 triệu"
- `quantity`: Số lượng sản phẩm/dịch vụ

### 3. Công thức tính toán

**Voice - Tổng thu chi:**

- Tổng thu nhập = Σ (`amount` × `quantity`) của tất cả incomes
- Tổng chi tiêu = Σ (`amount` × `quantity`) của tất cả expenses

**Bill - Tổng hóa đơn:**

- Thành tiền = `amount_after_discount` × `quantity`
- Tổng hóa đơn = Σ (thành tiền) của tất cả expenses
- Tổng giảm giá = Σ (`discount` × `quantity`) của tất cả expenses

### 4. Validation Rules

- ✅ Tất cả `amount`, `discount`, `amount_after_discount` phải **>= 0**
- ✅ `amount_after_discount` = `amount` - `discount` (phải tính đúng)
- ✅ `voice_id` và `bill_id` phải **unique**
- ✅ `transaction_type` chỉ chấp nhận **"income"** hoặc **"expense"**
- ✅ `money_type` chỉ chấp nhận **"VND"**, **"USD"**, hoặc **"EUR"**
- ✅ `quantity` phải **>= 0**
- ✅ `total_amount` phải bằng tổng của tất cả transactions tương ứng

### 5. Best Practices

1. **Format amount_string**:

   - Luôn sử dụng hàm `format_vnd_general()` từ `app/utils.py`
   - Ví dụ: 3000000 → "3 triệu", 550000 → "550 nghìn"

2. **Validate dữ liệu**:

   - Kiểm tra `amount_after_discount` = `amount` - `discount`
   - Kiểm tra `total_amount` = tổng của tất cả transactions

3. **UTC Timestamp**:

   - Luôn sử dụng UTC cho `utc_time`
   - Field này tự động set khi tạo document

4. **Bill Discount**:

   - Nếu không có discount, set `discount` = 0
   - Luôn tính `amount_after_discount` trước khi lưu

5. **Quantity**:

   - Mặc định = 1
   - Dùng > 1 cho nhiều sản phẩm cùng loại (ví dụ: 3 áo thun)

6. **Money Type**:
   - Mặc định là "VND"
   - Hiện tại chỉ support format VND qua `format_vnd_general()`

### 6. Hiển thị Bill dạng bảng

**Cột cơ bản (không có discount):**

- STT | Tên | Số Lượng | Giá | Thành tiền

**Cột đầy đủ (có discount):**

- STT | Tên | Số Lượng | Giá gốc | Giảm giá | Giá sau giảm | Thành tiền

**Footer:**

- Tổng giảm giá (nếu có)
- Tổng thanh toán/Tổng cộng

### 7. Common Mistakes cần tránh

❌ **SAI:**

- Quên nhân với `quantity` khi tính total
- `amount_after_discount` không khớp với `amount - discount`
- Dùng format số tiền không đúng (ví dụ: "3000000 VND" thay vì "3 triệu")
- `total_amount` không bằng tổng transactions

✅ **ĐÚNG:**

- Luôn nhân với `quantity` khi tính tổng
- Validate `amount_after_discount` trước khi lưu
- Dùng `format_vnd_general()` để format
- Kiểm tra `total_amount` = sum of all transactions

---

## 📊 Summary

| Model | Collection | Main Purpose                  | Has Income | Has Discount | Quantity Support |
| ----- | ---------- | ----------------------------- | ---------- | ------------ | ---------------- |
| Voice | Voices     | Ghi nhận thu chi từ giọng nói | ✅         | ❌           | ✅               |
| Bill  | Bills      | Lưu hóa đơn mua sắm           | ❌         | ✅           | ✅               |

---

**Last Updated:** November 12, 2025  
**Version:** 2.1 (Notes only - No Python code)
