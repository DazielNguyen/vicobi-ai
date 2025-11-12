def format_vnd_general(amount: float) -> str:
    """
    Chuyển đổi số tiền (VND) sang dạng rút gọn tiếng Việt.
    Hỗ trợ từ đơn vị đồng -> nghìn -> triệu -> tỷ -> nghìn tỷ -> triệu tỷ
    
    Ví dụ:
        500 -> '500 đồng'
        15_000 -> '15 nghìn'
        550_000 -> '550 nghìn'
        1_250_000 -> '1,25 triệu'
        50_000_000 -> '50 triệu'
        2_000_000_000 -> '2 tỷ'
        1_500_000_000_000 -> '1,5 nghìn tỷ'
    """
    if amount < 0:
        return f"-{format_vnd_general(abs(amount))}"
    
    units = [
        ("đồng", 1),
        ("nghìn", 1_000),
        ("triệu", 1_000_000),
        ("tỷ", 1_000_000_000),
        ("nghìn tỷ", 1_000_000_000_000),
        ("triệu tỷ", 1_000_000_000_000_000),
    ]
    
    for i in range(len(units) - 1, -1, -1):
        name, value = units[i]
        if amount >= value:
            result = amount / value
            result_str = f"{result:.2f}".rstrip('0').rstrip('.')
            return f"{result_str} {name}"
    
    return f"{amount} đồng"
