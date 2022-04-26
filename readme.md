java -jar cg-brutaltester.jar -r "java -jar spring.jar" -p1 "python bot_sliver.py" -p2 "python bot_sliver_old.py" -t 3 -n 100

# Chiến thuật wood 2（づ￣ 3 ￣）づ ╭❤️ ～

Di chuyển 3 hero để giết bọ <(")

1. Chọn target monster để giết thỏa một trong 3 điểu kiện sau và gần base nhất:

   a) `monster.nearBase == 1 and monster.threatFor == 1`: monster đang di chuyển đến base

   b) `monster.nearBase == 0 and monster.threatFor == 1`: monster sẽ di chuyến đến base sau khoảng thời gian `t` nào đó.

   c) Còn 1 cách để chọn những monster có xu hướng tấn công base nữa là: dựa vào `(vx,vy)` để viết phương trình đường thẳng, xem đường thẳng đó có cắt đường tròn tâm `(base_x, base_y)` bán kính `5000` hay không. Nếu có thì monster đó chắc chắn sẽ tấn công base. Nhưng có vẻ như codingame đã code sẵn cho mình hàm này ở điều kiện b) rồi :v, đã kiểm tra 😎

   Nói cách khác: chọn những monster có xu hướng tấn công base mà khoảng cách gần với base nhất.

2. Chọn 3 monster thỏa điều kiện 1 tương ứng với 3 heroes. Nếu có ít hơn 3 monster thỏa đều kiện đó thì cho 2-3 heroes hấp diêm 1 monster luôn =))))

3. Nếu có monster nào cách base `X` (chọn 5500) đơn vị thì ưu tiên sử dụng cả 3 heroes để giết monster đó

4. Nếu k có target nào, di chuyển về `(base_x, base_y)` sao cho khoảng cách giữa hero và base là 3000.

-> Dễ dàng pass được rank với tỷ lệ thắng gần bằng 100% (tính trận hòa = thắng).

> Bay luôn lên bronze với strategy này.

# Chiến thuật bronze (❁´◡`❁)

Cho thêm 3 spell wind, shield, control. Map có sương mù.
