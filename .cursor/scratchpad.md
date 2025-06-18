# Background and Motivation

Tự động hóa review code giúp tiết kiệm thời gian, tăng chất lượng code, giảm lỗi và nâng cao trải nghiệm phát triển phần mềm. Mục tiêu là xây dựng một AI agent có thể tự động review các merge request trên GitLab, sử dụng LangChain, MCP server, và RAG để phân tích codebase, đưa ra nhận xét, cảnh báo và đề xuất cải tiến.

**Lưu ý:** Dự án sẽ được phát triển bằng Python script (.py), không sử dụng Jupyter Notebook để đảm bảo dễ dàng triển khai thực tế, quản lý code và mở rộng về sau. Jupyter Notebook phù hợp cho thử nghiệm, nhưng với mục tiêu xây dựng pipeline hoàn chỉnh, Python script là lựa chọn tối ưu.

**Khả năng mở rộng:** Dự án sẽ thiết kế linh hoạt để hỗ trợ nhiều loại AI agent/LLM như OpenAI, Claude, Gemini... miễn là có integration với LangChain. Người dùng có thể lựa chọn LLM phù hợp với nhu cầu và API key sẵn có.

# Key Challenges and Analysis

- Kết nối và cấu hình MCP server với GitLab (yêu cầu token, cài đặt server, bảo mật)
- Index codebase hiệu quả với RAG (chọn mô hình embedding, chia nhỏ code, lưu trữ vector)
- Tích hợp các tool MCP vào agent LangChain
- Tối ưu prompt và luồng review để feedback hữu ích, ngắn gọn, sát thực tế
- Đảm bảo agent có thể truy xuất, phân tích và phản hồi merge request tự động
- Kiểm thử toàn bộ pipeline (từ push MR đến nhận feedback AI)

# High-level Task Breakdown

1. **Chuẩn bị môi trường và cài đặt phụ thuộc**

   - Cài Python 3.8+, Node.js 16+, pip, npm
   - Cài các package: langchain, faiss-cpu, openai, mcp-use
   - Tiêu chí thành công: Chạy được lệnh import các package trên Python shell

2. **Thiết lập và chạy MCP GitLab server**

   - Clone repo mcp-gitlab, cài đặt, build và chạy server
   - Thiết lập biến môi trường GITLAB_API_TOKEN, GITLAB_API_URL
   - Tiêu chí thành công: MCP server chạy, có thể nhận request từ client

3. **Index codebase với RAG**

   - Sử dụng LangChain để load, split codebase, tạo embedding, lưu vào vector store (Chroma hoặc Faiss)
   - Tiêu chí thành công: Có thể truy vấn vector store và nhận về code snippet liên quan

4. **Tích hợp MCP client và tool vào agent**

   - Kết nối MCP client với server, load tool GitLab
   - Tiêu chí thành công: Agent có thể gọi tool để lấy thông tin MR từ GitLab

5. **Tích hợp RAG vào agent**

   - Tạo tool RAG cho phép agent truy xuất codebase theo truy vấn
   - Tiêu chí thành công: Agent có thể lấy code snippet liên quan khi review MR

6. **Khởi tạo và cấu hình agent LangChain**

   - Kết hợp tool MCP và RAG, khởi tạo agent với LLM (OpenAI hoặc local LLM)
   - Tiêu chí thành công: Agent nhận prompt và thực thi được các tool

7. **Viết prompt và pipeline review MR**

   - Thiết kế prompt cho agent review MR, lấy diff, truy xuất codebase, sinh feedback
   - Tiêu chí thành công: Agent trả về nhận xét, cảnh báo, đề xuất cải tiến cho MR

8. **Kiểm thử end-to-end**
   - Tạo MR test, chạy agent, kiểm tra feedback
   - Tiêu chí thành công: Nhận được feedback AI trên MR, feedback hợp lý

# Project Status Board

- [x] Chuẩn bị môi trường và cài đặt phụ thuộc
- [x] Thiết lập và chạy MCP GitLab server ✓
- [x] Index codebase với RAG ✓
- [ ] Tích hợp MCP client và tool vào agent (Chuẩn bị thực hiện)
- [ ] Tích hợp RAG vào agent
- [ ] Khởi tạo và cấu hình agent LangChain
- [ ] Viết prompt và pipeline review MR
- [ ] Kiểm thử end-to-end

# Executor's Feedback or Assistance Requests

- Đã hoàn thành index codebase với RAG thành công
- Vector store đã được tạo và test queries hoạt động tốt
- Chuẩn bị chuyển sang bước 4: Tích hợp MCP client và tool vào agent
- Lưu ý: Giữ MCP GitLab server chạy cho các bước tiếp theo

# Lessons

- Đọc kỹ file trước khi chỉnh sửa
- Ghi chú debug vào output chương trình
- Nếu gặp cảnh báo bảo mật, chạy npm audit trước khi tiếp tục
- Luôn hỏi trước khi dùng lệnh git -force
- Khi gặp lỗi biến môi trường, có thể export trực tiếp trong terminal thay vì dùng file .env
- Khi sử dụng HuggingFace Embeddings, cần cài thêm package sentence-transformers
- Cập nhật imports để sử dụng phiên bản mới nhất của các package (tránh deprecated warnings)
