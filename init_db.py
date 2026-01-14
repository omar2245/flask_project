from app import db
try:
    db.create_all()
    print("資料庫初始化完成！")
except Exception as e:
    print("資料庫已存在或發生錯誤:", e)
