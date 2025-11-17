"""
SQLite数据库操作模块
使用SQLAlchemy ORM方式访问数据库
"""
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

# 创建基类
Base = declarative_base()


class AudioRecord(Base):
    """音频记录表模型"""
    __tablename__ = 'audio_records'
    
    id = Column(Integer, primary_key=True, autoincrement=True, comment='主键ID')
    text = Column(String(1000), nullable=False, comment='文本内容')
    preurl = Column(String(500), nullable=True, comment='预签名URL')
    path = Column(String(300), nullable=True, comment='文件路径')
    uptime = Column(DateTime, default=datetime.now, comment='上传时间')
    expire_time = Column(DateTime, nullable=True, comment='过期时间')
    
    def __repr__(self):
        return f"<AudioRecord(id={self.id}, text='{self.text[:30]}...', path='{self.path}')>"
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'text': self.text,
            'preurl': self.preurl,
            'path': self.path,
            'uptime': self.uptime.strftime('%Y-%m-%d %H:%M:%S') if self.uptime else None,
            'expire_time': self.expire_time.strftime('%Y-%m-%d %H:%M:%S') if self.expire_time else None,
        }


class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self, db_path='audio_records.db'):
        """
        初始化数据库管理器
        
        Args:
            db_path: 数据库文件路径
        """
        self.db_path = db_path
        self.engine = create_engine(f'sqlite:///{db_path}', echo=False)
        self.Session = sessionmaker(bind=self.engine)
        
        # 创建所有表
        Base.metadata.create_all(self.engine)
        print(f"✅ 数据库已初始化: {db_path}")
    
    def get_session(self):
        """获取数据库会话"""
        return self.Session()
    
    def add_record(self, text, preurl=None, path=None, expire_time=None):
        """
        添加一条记录
        
        Args:
            text: 文本内容
            preurl: 预签名URL
            path: 文件路径
            expire_time: 过期时间
            
        Returns:
            AudioRecord: 创建的记录对象
        """
        session = self.get_session()
        try:
            record = AudioRecord(
                text=text,
                preurl=preurl,
                path=path,
                expire_time=expire_time
            )
            session.add(record)
            session.commit()
            session.refresh(record)  # 刷新以获取自动生成的ID
            print(f"✅ 添加记录成功! ID: {record.id}")
            return record
        except Exception as e:
            session.rollback()
            print(f"❌ 添加记录失败: {e}")
            return None
        finally:
            session.close()
    
    def get_record_by_id(self, record_id):
        """
        根据ID获取记录
        
        Args:
            record_id: 记录ID
            
        Returns:
            AudioRecord or None
        """
        session = self.get_session()
        try:
            record = session.query(AudioRecord).filter(AudioRecord.id == record_id).first()
            return record
        finally:
            session.close()
    
    def get_all_records(self, limit=None):
        """
        获取所有记录
        
        Args:
            limit: 限制返回数量，默认返回全部
            
        Returns:
            list: 记录列表
        """
        session = self.get_session()
        try:
            query = session.query(AudioRecord).order_by(AudioRecord.uptime.desc())
            if limit:
                query = query.limit(limit)
            records = query.all()
            return records
        finally:
            session.close()
    
    def update_record(self, record_id, **kwargs):
        """
        更新记录
        
        Args:
            record_id: 记录ID
            **kwargs: 要更新的字段，如 text='新文本', preurl='新URL'
            
        Returns:
            bool: 更新成功返回True
        """
        session = self.get_session()
        try:
            record = session.query(AudioRecord).filter(AudioRecord.id == record_id).first()
            if record:
                for key, value in kwargs.items():
                    if hasattr(record, key):
                        setattr(record, key, value)
                session.commit()
                print(f"✅ 更新记录成功! ID: {record_id}")
                return True
            else:
                print(f"❌ 记录不存在: ID {record_id}")
                return False
        except Exception as e:
            session.rollback()
            print(f"❌ 更新记录失败: {e}")
            return False
        finally:
            session.close()
    
    def delete_record(self, record_id):
        """
        删除记录
        
        Args:
            record_id: 记录ID
            
        Returns:
            bool: 删除成功返回True
        """
        session = self.get_session()
        try:
            record = session.query(AudioRecord).filter(AudioRecord.id == record_id).first()
            if record:
                session.delete(record)
                session.commit()
                print(f"✅ 删除记录成功! ID: {record_id}")
                return True
            else:
                print(f"❌ 记录不存在: ID {record_id}")
                return False
        except Exception as e:
            session.rollback()
            print(f"❌ 删除记录失败: {e}")
            return False
        finally:
            session.close()
    
    def search_by_text(self, keyword):
        """
        根据文本内容搜索
        
        Args:
            keyword: 搜索关键词
            
        Returns:
            list: 匹配的记录列表
        """
        session = self.get_session()
        try:
            records = session.query(AudioRecord).filter(
                AudioRecord.text.like(f'%{keyword}%')
            ).all()
            return records
        finally:
            session.close()
    
    def get_expired_records(self):
        """
        获取已过期的记录
        
        Returns:
            list: 过期的记录列表
        """
        session = self.get_session()
        try:
            now = datetime.now()
            records = session.query(AudioRecord).filter(
                AudioRecord.expire_time < now
            ).all()
            return records
        finally:
            session.close()


# 使用示例
if __name__ == "__main__":
    from datetime import timedelta
    
    print("="*70)
    print("SQLite数据库操作演示")
    print("="*70)
    
    # 1. 创建数据库管理器
    db = DatabaseManager('audio_records.db')
    
    # 2. 添加记录
    print("\n【1. 添加记录】")
    record1 = db.add_record(
        text="Hello, this is a test audio.",
        preurl="https://example.com/signed-url-1",
        path="/path/to/audio1.wav",
        expire_time=datetime.now() + timedelta(hours=1)
    )
    
    record2 = db.add_record(
        text="Another audio record for testing.",
        preurl="https://example.com/signed-url-2",
        path="/path/to/audio2.wav",
        expire_time=datetime.now() + timedelta(days=1)
    )
    
    # 3. 查询单条记录
    print("\n【2. 查询单条记录】")
    if record1:
        found = db.get_record_by_id(record1.id)
        if found:
            print(f"找到记录: {found}")
            print(f"字典格式: {found.to_dict()}")
    
    # 4. 查询所有记录
    print("\n【3. 查询所有记录】")
    all_records = db.get_all_records()
    print(f"共有 {len(all_records)} 条记录:")
    for record in all_records:
        print(f"  - ID:{record.id}, 文本:{record.text[:30]}..., 路径:{record.path}")
    
    # 5. 更新记录
    print("\n【4. 更新记录】")
    if record1:
        db.update_record(
            record1.id,
            text="Updated text content",
            preurl="https://example.com/new-signed-url"
        )
    
    # 6. 搜索记录
    print("\n【5. 搜索记录】")
    results = db.search_by_text("test")
    print(f"包含'test'的记录有 {len(results)} 条:")
    for record in results:
        print(f"  - {record.text}")
    
    # 7. 获取过期记录
    print("\n【6. 获取过期记录】")
    expired = db.get_expired_records()
    print(f"过期记录有 {len(expired)} 条")
    
    # 8. 删除记录（注释掉，避免删除演示数据）
    # print("\n【7. 删除记录】")
    # if record2:
    #     db.delete_record(record2.id)
    
    print("\n" + "="*70)
    print("✅ 演示完成！数据库文件: audio_records.db")
    print("="*70)

