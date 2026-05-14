# Flask Social API

這是一個以 Flask 建立的社群平台後端 API 專案，實作使用者註冊登入、JWT 驗證、貼文、留言、按讚、追蹤、個人資料更新、圖片上傳、分頁查詢與雲端部署等常見後端功能。

本專案的目標是展示後端工程能力，不只是完成 CRUD，而是把驗證、資料模型設計、權限控管、資料關聯、錯誤處理、檔案上傳與部署流程整理成一個可維護的 RESTful API 服務。

## 專案重點

- 使用 Flask 建立 RESTful API，並以 `/api/v1` 做 API 版本管理。
- 使用 SQLAlchemy 建立關聯式資料模型。
- 使用 Flask-Migrate 管理資料庫 migration。
- 使用 bcrypt 儲存密碼雜湊，不保存明文密碼。
- 使用 JWT access token / refresh token 實作登入驗證。
- 對貼文、留言更新與刪除加入擁有者權限檢查。
- 使用唯一約束避免重複按讚與重複追蹤。
- 使用 Cloudinary 處理頭像與貼文圖片上傳。
- 使用分頁設計處理貼文、留言、追蹤列表與按讚列表。
- 提供 Docker、Gunicorn、Google Cloud Run 與 Render 部署設定。

## 技術棧

| 類別 | 技術 |
| --- | --- |
| Web Framework | Flask 3 |
| Database | PostgreSQL |
| ORM | SQLAlchemy |
| Migration | Flask-Migrate / Alembic |
| Authentication | Flask-JWT-Extended |
| Password Hashing | bcrypt |
| Image Upload | Cloudinary |
| Image Validation | Pillow |
| Deployment | Docker, Gunicorn, Google Cloud Run, Render |
| Config | python-dotenv, environment variables |

## 專案架構

```text
flask_project/
|-- app.py                  # Flask app 初始化、套件設定、Blueprint 註冊
|-- controllers/            # API 商業邏輯與資料處理
|-- routes/                 # API 路由定義
|-- models/                 # SQLAlchemy 資料模型
|-- migrations/             # 資料庫 migration
|-- utils/                  # 共用工具
|-- Dockerfile              # Docker image 設定
|-- cloudbuild.yaml         # GCP Cloud Build / Cloud Run 部署設定
|-- render.yaml             # Render 部署設定
`-- requirements.txt        # Python 套件依賴
```

專案採用 routes 與 controllers 分層：

- `routes/` 負責定義 API path、HTTP method 與是否需要 JWT 驗證。
- `controllers/` 負責 request validation、資料庫操作、權限檢查與 response 格式。
- `models/` 負責資料表欄位、關聯、cascade 與 unique constraint 設計。

## 資料模型設計

主要資料表：

| Model | 說明 |
| --- | --- |
| `User` | 使用者帳號、Email、密碼雜湊、頭像、個人簡介 |
| `Post` | 使用者貼文內容 |
| `PostImage` | 貼文圖片 URL |
| `Comment` | 貼文留言 |
| `PostLikes` | 貼文按讚關聯 |
| `CommentLikes` | 留言按讚關聯 |
| `Follow` | 使用者追蹤關聯 |

設計重點：

- `Post` 與 `Comment`、`PostLikes`、`PostImage` 設定 cascade，刪除貼文時會清理相關資料。
- `PostLikes` 使用 `(user_id, post_id)` unique constraint，避免同一位使用者重複按讚同一篇貼文。
- `CommentLikes` 使用 `(user_id, comment_id)` unique constraint，避免留言重複按讚。
- `Follow` 使用 `(follower_id, following_id)` unique constraint，避免重複追蹤。
- 貼文列表查詢會彙整 likes count、comments count 與目前使用者是否已按讚，讓前端可直接渲染列表狀態。

## API 功能

### Auth

| Method | Endpoint | 權限 | 說明 |
| --- | --- | --- | --- |
| POST | `/api/v1/auth/register` | 不需登入 | 使用者註冊 |
| POST | `/api/v1/auth/login` | 不需登入 | 使用者登入，回傳 access token 與 refresh token |
| POST | `/api/v1/auth/refresh` | Refresh token | 更新 access token |
| POST | `/api/v1/auth/logout` | Refresh token | 登出 |

### User

| Method | Endpoint | 權限 | 說明 |
| --- | --- | --- | --- |
| GET | `/api/v1/user/me` | 需登入 | 取得目前登入使用者資料 |
| PUT | `/api/v1/user/me` | 需登入 | 更新目前登入使用者資料 |
| POST | `/api/v1/user/me/upload_avatar` | 需登入 | 上傳使用者頭像 |
| GET | `/api/v1/user/<user_id>` | 不需登入 | 取得指定使用者公開資料 |
| POST | `/api/v1/user<user_id>/follow` | 需登入 | 追蹤使用者 |
| DELETE | `/api/v1/user<user_id>/unfollow` | 需登入 | 取消追蹤使用者 |
| GET | `/api/v1/user<user_id>/following` | 不需登入 | 取得使用者正在追蹤的列表 |
| GET | `/api/v1/user<user_id>/follower` | 不需登入 | 取得使用者的粉絲列表 |
| GET | `/api/v1/user/<user_id>/posts` | 可選登入 | 取得指定使用者的貼文 |
| GET | `/api/v1/user/<user_id>/follows/stat` | 不需登入 | 取得追蹤數與粉絲數 |
| GET | `/api/v1/user/<target_user_id>/is_following` | 需登入 | 檢查目前使用者是否追蹤指定使用者 |

### Post

| Method | Endpoint | 權限 | 說明 |
| --- | --- | --- | --- |
| POST | `/api/v1/posts` | 需登入 | 建立貼文 |
| GET | `/api/v1/posts?page=1&limit=10` | 可選登入 | 取得貼文列表 |
| GET | `/api/v1/posts/<post_id>` | 可選登入 | 取得貼文詳細資料 |
| PUT | `/api/v1/posts/<post_id>` | 需登入 | 更新自己的貼文 |
| DELETE | `/api/v1/posts/<post_id>` | 需登入 | 刪除自己的貼文 |
| GET | `/api/v1/posts/<post_id>/comments` | 可選登入 | 取得貼文留言 |
| POST | `/api/v1/posts/<post_id>/like` | 需登入 | 對貼文按讚 |
| DELETE | `/api/v1/posts/<post_id>/unlike` | 需登入 | 取消貼文按讚 |
| GET | `/api/v1/posts/<post_id>/like` | 需登入 | 取得貼文按讚使用者列表 |

### Comment

| Method | Endpoint | 權限 | 說明 |
| --- | --- | --- | --- |
| POST | `/api/v1/comments` | 需登入 | 建立留言 |
| PUT | `/api/v1/comments/<comment_id>` | 需登入 | 更新自己的留言 |
| DELETE | `/api/v1/comments/<comment_id>` | 需登入 | 刪除自己的留言 |
| POST | `/api/v1/comments/<comment_id>/like` | 需登入 | 對留言按讚 |
| DELETE | `/api/v1/comments/<comment_id>/unlike` | 需登入 | 取消留言按讚 |
| GET | `/api/v1/comments/<comment_id>/like` | 需登入 | 取得留言按讚使用者列表 |

## 驗證流程

1. 使用者註冊帳號，輸入 username、email、password。
2. 後端驗證欄位格式與帳號是否重複。
3. 密碼使用 bcrypt hash 後寫入資料庫。
4. 使用者登入後，後端回傳 access token 與 refresh token。
5. 需要登入的 API 透過 `Authorization: Bearer <access_token>` 驗證身份。
6. access token 過期後，可透過 refresh token 取得新的 access token。

## 圖片上傳設計

本專案使用 Cloudinary 作為圖片儲存服務：

- 使用者頭像上傳後會存入 `avatars` folder。
- 貼文圖片上傳後會存入 `posts` folder。
- 上傳前會使用 Pillow 驗證檔案是否為有效圖片。
- 頭像限制檔案大小為 2MB。
- 貼文圖片最多可一次上傳 2 張。
- Cloudinary transformation 會限制圖片尺寸，降低前端載入壓力。

## 環境變數

請在專案根目錄建立 `.env`：

```env
SECRET_KEY=your_flask_secret
JWT_SECRET_KEY=your_jwt_secret
SQLALCHEMY_DATABASE_URI=postgresql://user:password@host:5432/database
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret
PORT=8080
FLASK_DEBUG=True
```

## 本機開發

### 1. 建立虛擬環境

```bash
python -m venv .venv
.\.venv\Scripts\activate
```

### 2. 安裝套件

```bash
pip install -r requirements.txt
```

### 3. 設定環境變數

建立 `.env` 並填入資料庫連線、JWT secret 與 Cloudinary 金鑰。

### 4. 執行 migration

```bash
flask db upgrade
```

### 5. 啟動服務

```bash
python app.py
```

預設服務位置：

```text
http://localhost:8080
```

## Docker 執行

```bash
docker build -t flask-social-api .
docker run --env-file .env -p 8080:8080 flask-social-api
```

Dockerfile 使用 `python:3.11-slim`，並透過 Gunicorn 啟動 Flask app：

```bash
gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 app:app
```

## 部署

### Google Cloud Run

專案包含 `cloudbuild.yaml`，可透過 Cloud Build 建置 Docker image 並部署到 Cloud Run：

```bash
gcloud builds submit --config=cloudbuild.yaml . --substitutions=_REGION=us-central1
```

部署流程：

1. 使用 Docker 建立 image。
2. 將 image push 到 Google Container Registry。
3. 將服務部署到 Cloud Run。

正式環境建議將以下資訊設定在 Cloud Run environment variables 或 Secret Manager：

- `SECRET_KEY`
- `JWT_SECRET_KEY`
- `SQLALCHEMY_DATABASE_URI`
- `CLOUDINARY_CLOUD_NAME`
- `CLOUDINARY_API_KEY`
- `CLOUDINARY_API_SECRET`

### Render

專案也提供 `render.yaml`：

```yaml
buildCommand: pip install -r requirements.txt
startCommand: gunicorn app:app
```

部署到 Render 前，需先在 Render dashboard 設定環境變數。

## API 使用範例

### 註冊

```bash
curl -X POST http://localhost:8080/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"demo_user\",\"email\":\"demo@example.com\",\"password\":\"password123\"}"
```

### 登入

```bash
curl -X POST http://localhost:8080/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"demo_user\",\"password\":\"password123\"}"
```

### 建立貼文

```bash
curl -X POST http://localhost:8080/api/v1/posts \
  -H "Authorization: Bearer <access_token>" \
  -F "content=Hello backend" \
  -F "images=@./example.jpg"
```

## 工程亮點

- 將 API 按照 Auth、User、Post、Comment 拆分 Blueprint。
- Controller 層集中處理 validation、permission check 與 database transaction。
- 使用 `db.session.rollback()` 處理資料庫寫入失敗情境。
- 使用 optional JWT 讓公開 API 也能根據登入狀態回傳 `is_liked`。
- 使用分頁避免列表 API 一次回傳過多資料。
- 使用 relational constraint 保護資料一致性。
- 使用 Cloudinary 解耦本機檔案儲存與部署環境。
- 使用 Docker 與 Gunicorn 讓服務更接近正式部署情境。

## 未來優化方向

- 補上 pytest，自動測試註冊、登入、權限、貼文與留言流程。
- 加入 Marshmallow 或 Pydantic 做 request schema validation。
- 補上 OpenAPI / Swagger 文件。
- 加入 rate limiting，保護登入與圖片上傳 API。
- 加入 structured logging，方便正式環境追蹤錯誤。
- 加入 CI workflow，在 push 或 pull request 時自動執行測試與 lint。
