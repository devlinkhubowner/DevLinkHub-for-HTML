#データベース用ライブラリー
from supabase import Client, create_client#supabase操作用 MIT
import os#環境変数用
from dotenv import load_dotenv#環境変数用 　BSD-3-Clause
import json#supabaseのdataをjsonに変換用
#app用
import traceback

class supabaseError(Exception):
    pass

class supabase():
    def __init__(self,url,key):
        self.__supabase: Client = create_client(url,key)
    def newdata(self,table,data,column):#新しいdataを保存する
        try:
            if isinstance(data,dict):
                response = (
                    self.__supabase.table(table)
                    .insert({column:data})
                    .execute()
                )
            else:
                response = (
                    self.__supabase.table(table)
                    .insert({column:data})
                    .execute()
                )
            if response.data == []:
                raise supabaseError("保存するdataが空でした(newdata)")
        except Exception:
            raise supabaseError(traceback.format_exc())
        
    def allread(self,table):#テーブル内にあるすべてのdataを取得する
        try:
            response = (
                self.__supabase.table(table)
                .select("*")#テーブルの全てdataを選択
                .execute()
            )
            jsondata = json.dumps(response.data,ensure_ascii=False,indent=2)#ensure_ascii=Falseすることにより日本語記号などもそのまま描画する,indent=2人間に読みやすいようにする
            response = json.loads(jsondata)#strからjsonに変換
        except Exception:
            raise supabaseError(traceback.format_exc())
        else:
            return response
        
    def searchread(self, table, search, key):
        datas = self.allread(table)
        try:
            for data in datas:
                value = data.get(key)
                # 文字列同士で比較するように変換
                if isinstance(value, str) and isinstance(search, str):
                    if search in value:
                        return data
            return False
        except Exception as e:
            raise supabaseError(traceback.format_exc())


    def delete(self, table, id,number):
        try:
            response = (
                self.__supabase.table(table)
                .delete()
                .eq(id,number)  # 例: key="profile->>name", value="Taro"
                .execute()
            )
        except Exception:
            raise supabaseError(traceback.format_exc())

    def json(self, table, data, former,overwrite,column):
        try:
            if column == None:
                column = table
            response = (
                self.__supabase.table(table)
                .update({overwrite:data})
                .eq(f"{table}->>{table}",former)  # 例: key="profile->>name", value="Taro"
                .execute()
            )
            if response.data == []:
                raise supabaseError(f"保存するdataが空でした(update) table:{table},former:{former},data:{data},column{column},overwrite:{overwrite}")
        except Exception:
            raise supabaseError(traceback.format_exc())

    def text(self,table,data,former,column,columneq):
        try:
            if column == None:
                column = table
            response = (
                self.__supabase.table(table)
                .update({column:data})
                .eq(columneq, former)
                .execute()
            )
            if response.data == []:
                raise supabaseError(f"保存するdataが空でした(update) table:{table},former:{former},columneq:{columneq},data:{data},column:{column}")
        except Exception:
            raise supabaseError(traceback.format_exc())

# #初期設定
load_dotenv()#envファイルのload
supabase = supabase(url=os.getenv("supabaseurl"),key=os.getenv("supabasekey"))