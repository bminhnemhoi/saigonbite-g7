// Speaker notes (Vietnamese) – Presentation 2 Design Review, 19 slides, target about 9:30–9:50 including a short Figma demo.
// (✂) = câu có thể bỏ nếu chậm hơn mốc giờ.
module.exports = [
`SLIDE 1 · MỞ ĐẦU · KHÁNH · 0:00 → 0:25
Dạ em chào thầy. Nhóm G7 trình bày Part 2 – thiết kế SaigonBite. Em là Lê Xuân Khánh, phụ trách UC1 Place and Manage Orders; bạn Ngô Bình Minh phụ trách UC2 Manage Hubs and Capacity. Nhóm làm Tier 4 như thầy đã đồng ý ở buổi trước.`,
`SLIDE 2 · THAY ĐỔI SAU PART 1 · KHÁNH · 0:25 → 0:55
Report đã lên bản 2.0 với ba yêu cầu Tier 4: FR36 PayPal sandbox thật – em làm; FR37 dashboard Admin – Minh làm; NFR7 test Playwright – cả nhóm. Mọi thay đổi ghi trong Feedback Log và Team Workbook. (✂) Thứ tự hôm nay ở khung bên phải.`,
`SLIDE 3 · USE CASE · MINH · 0:55 → 1:30
Dạ em là Minh. Customer là actor trừu tượng; Local Customer và Foreign Tourist kế thừa nên cùng dùng UC1, chỉ khác đăng ký và thanh toán – BR18. UC1 màu cam của Khánh, UC2 màu xanh của em, mỗi use case đủ CRUD. Tính giá và chọn thanh toán là «include»; trả PayPal sandbox là «extend», chỉ chạy khi khách du lịch chọn PayPal.`,
`SLIDE 4 · UC1 PIPELINE · KHÁNH · 1:30 → 2:10
Một lần đặt đơn đi qua 7 bước: controller chỉ nhận dữ liệu; HubLoadService kiểm tải, từ 90% thì từ chối; PricingService tính giá theo BR10; resolver chọn phương thức theo loại khách; cuối cùng lưu tất cả trong một transaction. Ba nhánh phụ: bếp đầy thì gợi ý bếp khác trong 8 km; sửa đơn thì tính lại theo snapshot; thanh toán lỗi thì rollback.`,
`SLIDE 5 · UC1 SEQUENCE 2/2 · KHÁNH · 2:10 → 2:40
Resolver chặn phương thức của nhóm khách khác và COD trên 1 triệu trước khi lưu. Sau đó mở transaction, state machine ghi lịch sử đầu tiên, strategy thanh toán. Với PayPal, strategy trả ApprovalRequired, khách duyệt trên sandbox rồi quay lại để capture.`,
`SLIDE 6 · UC2 · MINH · 2:40 → 3:20
UC2 của em xoay quanh tải bếp. Create: sức chứa là số nguyên dương. Read: tải bằng đơn Confirmed cộng Preparing chia sức chứa, không làm tròn, chia ba vùng. Update: đổi sức chứa thì luật giảm giá và chặn đơn áp dụng ngay. Delete là soft-delete: như sequence bên phải, hub còn đơn đang chạy thì bị chặn – giả định A-07.`,
`SLIDE 7 · STATE MACHINE · KHÁNH · 3:20 → 3:50
Tám trạng thái, mỗi mũi tên ghi ai được chuyển và điều kiện. Bảng chuyển nằm trong OrderStateMachine ở business layer, giao diện chỉ ẩn nút. Mỗi lần chuyển ghi lịch sử, và 15 test chuyển sai đã có trong workbook.`,
`SLIDE 8 · CRC → CLASS · MINH · 3:50 → 4:30
Nhóm viết CRC trước để thống nhất ai làm gì: OrderService điều phối, PricingService tính giá, HubLoadService đo tải, OrderStateMachine đổi trạng thái, resolver chọn thanh toán, HubService là CRUD của em. Từ đó ra class diagram: User là gốc, Customer trừu tượng, Local và Tourist kế thừa – chung một schema; Order giữ snapshot và bảng giá.`,
`SLIDE 9 · STRATEGY · KHÁNH · 4:30 → 5:00
Một interface IPaymentStrategy, năm class cho năm phương thức, resolver chọn theo loại khách – BR13. Thêm phương thức mới chỉ là một class và một dòng đăng ký như bên phải, không sửa class cũ – sẵn sàng cho Change Request tuần 5.`,
`SLIDE 10 · DATABASE · MINH · 5:00 → 5:35
Users chung cho hai loại khách, mỗi loại một bảng profile – table-per-type. Mỗi đơn lưu snapshot và toàn bộ S, Q, V, D, R, R2, Total nên giá luôn tái lập được. Dữ liệu đã gắn với đơn chỉ soft-delete. Lịch sử trạng thái chỉ thêm, không sửa; RowVersion chặn hai người cùng chuyển một đơn.`,
`SLIDE 11 · KIẾN TRÚC · KHÁNH · 5:35 → 6:00
Ba lớp MVC: presentation chỉ có view, controller, view model và phân quyền; business layer chứa toàn bộ luật; data layer là EF Core và SQL Server. PayPal chỉ được gọi từ một strategy. Mỗi khối gắn NFR mà nó đáp ứng.`,
`SLIDE 12 · NƠI ĐẶT LUẬT GIÁ · KHÁNH · 6:00 → 6:25
Luật giá chỉ nằm trong PricingService, đúng thứ tự BR10, làm tròn một lần. Hai ví dụ dưới là số trong prototype: 205 nghìn và 269 nghìn. Mỗi bước là một hàm riêng nên test EP, BVA được từng ngưỡng.`,
`SLIDE 13 · TIER 4 · KHÁNH (a) → MINH (b, c) · 6:25 → 7:05
KHÁNH: Phần a – PayPal sandbox thật theo Orders v2: tạo đơn, khách duyệt, capture, hoàn tiền khi hủy. Chỉ một strategy gọi PayPal, khóa bí mật để trong user secrets. Nghiệm thu: capture ID lưu trên đơn.
MINH: Phần b – dashboard của em: KPI, tải bếp trực tiếp, bộ lọc và công tắc mưa; nghiệm thu là số khớp R1, R2. Phần c – bảy test Playwright như danh sách, chạy headless, phải đạt 100% và có báo cáo HTML.`,
`SLIDE 14 · UI/UX 4 GIAI ĐOẠN · MINH · 7:05 → 7:25
Giao diện qua bốn giai đoạn: sketch, wireframe, mockup và prototype có vùng bấm, trên lưới Bootstrap. File Figma có đủ các trang tương ứng và trang thương hiệu.`,
`SLIDE 15 · LANDING PAGE · MINH · 7:25 → 7:45
Landing page dùng ảnh thật Sài Gòn về đêm, có zoom chậm, đếm số, hiện dần khi cuộn và băng chuyền món. Ngay trên trang đã giải thích bếp vắng giảm 10% và ví dụ giá 205 nghìn. Video hiệu ứng nằm trong thư mục _extras.`,
`SLIDE 16 · HÀNH TRÌNH KHÁCH HÀNG · MINH · 7:45 → 8:10
Khách chọn bếp theo vùng tải, xem thực đơn ba thương hiệu, thanh toán với từng dòng giá có mã luật, rồi theo dõi đơn kèm snapshot giá và quy tắc hủy.`,
`SLIDE 17 · VẬN HÀNH · MINH · 8:10 → 8:35
Phía vận hành: dashboard Tier 4, danh sách hub của UC2 với tải chưa làm tròn, báo cáo R1, và checkout của khách du lịch trả PayPal – tổng 269 nghìn có voucher, mưa và miễn phí giao.`,
`SLIDE 18 · MOBILE + DEMO FIGMA · MINH · 8:35 → 9:30
Cùng giao diện trên điện thoại 390 pixel, không cuộn ngang. [Mở Figma, trang 05 Prototype, bấm Present] Luồng 1: landing, đăng nhập, chọn bếp, thanh toán tiền mặt. Luồng 2: khách du lịch trả PayPal sandbox. Luồng 3: Admin xem dashboard, hub và báo cáo.`,
`SLIDE 19 · KẾT · MINH · 9:30 → 9:50
Part 3 nhóm làm đúng thiết kế: tuần 5 skeleton và Change Request, tuần 6 hoàn thành UC1, UC2, test giá, PayPal, dashboard, tuần 7 Playwright, RTM, báo cáo và demo. Nhóm em cảm ơn thầy và xin nghe câu hỏi.`,
];
