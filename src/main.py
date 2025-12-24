#web用
from fastapi import FastAPI,WebSocket,WebSocketDisconnect,Request,HTTPException,Response,APIRouter
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse,RedirectResponse
from fastapi.staticfiles import StaticFiles
from typing import List
import uvicorn#fastapi実行用

#githubapp用
import sys
import time
import os
import jwt
import asyncio

# その他
import json
import tracemalloc
import httpx

#外部ファイル
import kit#すべてのファイルをまとめたもの

class Websocketerror(Exception):
    pass

if __name__ == "__main__":
    serverdata = "Servers";messagedata = "Messages";channeldata = "channel";openchat = "openchat";memberlist = "memberlist";
else:
    serverdata = "test_Servers";messagedata = "test_Messages";channeldata = "test_channel";openchat = "test_openchat";memberlist = "test_memberlist"

app = FastAPI()#インスタンス作成
router = APIRouter()
templates = Jinja2Templates(directory="src/templates")#HTMLがあるファイルのload
app.mount("/static",StaticFiles(directory="src/static"),name="static")
tracemalloc.start()

#短命token(github apps)
async def get_jwt():
    if __name__ == "__main__":
        pem = os.getenv("app")  # 文字列で環境変数から取得
        client_id = "2110238"
    else:
        pem = os.getenv("apptest")
        client_id = "2110496"
    payload = {
        'iat': int(time.time()),  # 発行時刻
        'exp': int(time.time()) + 120,  #! 有効期限（2分）
        'iss': client_id,
    }

    encoded_jwt = jwt.encode(payload, pem, algorithm='RS256')
    if isinstance(encoded_jwt, bytes):
        encoded_jwt = encoded_jwt.decode("utf-8")

    # 実際にGitHub APIでApp情報を確認
    headers = {"Authorization": f"Bearer {encoded_jwt}", "Accept": "application/vnd.github.v3+json"}
    async with httpx.AsyncClient() as client:
        r = await client.get(url="https://api.github.com/app/installations", headers=headers, timeout=15.0)
        installations = r.json()
        if installations != []:
            token = installations
            avatar_url = installations[0]["account"]["avatar_url"]
            # JWTは今までのを使う
            r2 = await client.post(
                url=f"https://api.github.com/app/installations/{installations[0]['id']}/access_tokens",
                headers=headers,
                timeout=15.0,
            )
            return True, r2.json()["token"], token, avatar_url
        else:
            if __name__ == "__main__":
                return (f"https://github.com/apps/devlinkhub-app"), [], "", ""
            else:
                return (f"https://github.com/apps/devlinkhub-app-test"), [], "", ""

def _savemessage_sync(node_id, token, data, avatar_url):
    if __name__ != "__main__":
        key = os.getenv("apptest")
    else:
        key = os.getenv("app")
    #ストレージに保存
    data = json.dumps(data[0])
    data = json.loads(data)
    repos = kit.github.repository(installation_id=data["id"],appid=data["app_id"],key=key)
    if len(repos) == 1:
        search = kit.supabase.searchread(table=serverdata,search=node_id,key="username")["servers"].split("|")
        for server in search:
            server = kit.supabase.searchread(table=messagedata,search=node_id,key="username")
            if isinstance(server,dict):
                message = server["message"]
                filename = server["server"]
                channel = server["channel"]
            if server != False:
                file = kit.github.filepass(token=token,title=repos[0],searchpass=f"{filename}_{channel}.txt")
                if file is False:
                    kit.github.createfile(token=token,repo_name=repos[0],update_data=str(message),filepass=f"{filename}_{channel}.txt")
                else:
                    txt = kit.github.read(token=token,repo_name=repos[0],filepass=f"{filename}_{channel}.txt")
                    if txt["content"].strip() != "":
                        kit.github.update(token=token,repo_name=repos[0],update_data=f"{str(txt['content'])}|{str(message)}",filename=f"{filename}_{channel}.txt")
                    else:
                        kit.github.update(token=token,repo_name=repos[0],update_data=f"{str(message)}",filename=f"{filename}_{channel}.txt")
                server = json.dumps(server)
                server = json.loads(server)
                # kit.supabase.delete(table=messagedata,number=search["id"])
                return True,repos,avatar_url
            else:
                try:
                    kit.github.createfile(token=token,repo_name=repos[0],update_data=str(message),filepass=f"{filename}_{channel}.txt")
                except UnboundLocalError:
                    return True,repos,avatar_url

async def savemessage(node_id):
    cheak, token, data, avatar_url = await get_jwt()
    if cheak == True:
        result = await asyncio.to_thread(_savemessage_sync, node_id, token, data, avatar_url)
        if result is not None:
            return result
        else:
            if __name__ == "__main__":
                return RedirectResponse("https://github.com/apps/devlinkhub-app")
            else:
                return RedirectResponse("https://github.com/apps/devlinkhub-app-test")
    else:
        if __name__ == "__main__":
            return RedirectResponse("https://github.com/apps/devlinkhub-app")
        else:
            return RedirectResponse("https://github.com/apps/devlinkhub-app-test")

#refresh_token（長命）(github OAuth)
@router.get("/oauth2/login")
async def login(request: Request):
    if __name__ == "__main__":
        redirect_uri = "https://devlinkhub.onrender.com/oauth_callback"
    else:
        redirect_uri = "http://localhost:8000/oauth_callback"

    return RedirectResponse(
        f"https://github.com/login/oauth/authorize"
        f"?response_type=code"
        f"&client_id={os.getenv("GITHUB_CLIENT_ID")}"
        f"&redirect_uri={redirect_uri}"
        f"&scope=read%3Auser+user%3Aemail"
        f"&state=S_k62Mgwu_OPEGQqSWT3Iw"
    )

@router.get("/oauth_callback")
async def github_callback(request: Request,response:Response, code: str, state: str | None = None):
    if __name__ == "__main__":
        redirect_uri = "https://devlinkhub.onrender.com/oauth_callback"
    else:
        redirect_uri = "http://localhost:8000/oauth_callback"

    token_url = "https://github.com/login/oauth/access_token"

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            token_url,
            headers={"Accept": "application/json"},
            data={
                "client_id": os.getenv("GITHUB_CLIENT_ID"),
                "client_secret": os.getenv("GITHUB_CLIENT_SECRET"),
                "code": code,
                "redirect_uri": redirect_uri,  # 必ず login の redirect_uri と一致
                "state": state,
            },
            timeout=15.0,
        )

        token_json = resp.json()
        if "access_token" not in token_json:
            raise HTTPException(status_code=400, detail={"error": "トークン取得失敗", "response": token_json})

        access_token = token_json["access_token"]
        user_resp = await client.get(
            "https://api.github.com/user",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        user_data = user_resp.json()
        username = user_data.get("login")
        node_id = user_data.get("node_id")
        try:
            cheak,repos,avatar_url = await savemessage(node_id=node_id)
        except TypeError as e:
            if __name__ == "__main__":
                return RedirectResponse("https://github.com/apps/devlinkhub-app")
            else:
                return RedirectResponse("https://github.com/apps/devlinkhub-app-test")
        if cheak == True:
            # roomdata取得
            servers = kit.supabase.searchread(table=serverdata, search=node_id,key="username")
            if isinstance(servers,bool) or servers == None:
                pass
            else:
                servers = servers["servers"]
            response = templates.TemplateResponse("serverlist.html",{"request": request,"username": username, "servers": servers})

            response.set_cookie(
                key="access_token",
                value=access_token,
                max_age=3600,
                httponly=True
            )

            response.set_cookie(
                key="node_id",
                value=node_id,
                max_age=3600,
                httponly=True,
            )
            response.set_cookie(
                key="repo",
                value=repos[0],
                max_age=3600,
                httponly=True
            )
            print(avatar_url)
            response.set_cookie(
                key="image",
                value=avatar_url,
                max_age=3600,
                httponly=True
            )

            response.set_cookie(
                key="username",
                value=username,
                max_age=3600,
                httponly=True
            )

            return response
        else:
            return RedirectResponse(cheak)

@app.get("/", response_class=HTMLResponse)#homepageの描画
async def root(request: Request):
    return templates.TemplateResponse("index.html",{"request": request})

@app.get("/serverlist",response_class=HTMLResponse)#serverリストのHTML
async def serverlist(request: Request):
    server = kit.supabase.searchread(table=serverdata,search=request.cookies.get("node_id"),key="username")["servers"]
    return templates.TemplateResponse("serverlist.html",{"request": request,"servers":server,"username":request.cookies.get("username")})

@app.get("/server/",response_class=HTMLResponse)#serverのチャンネル描画
async def server(request: Request,name:str):
    server = kit.supabase.searchread(table=channeldata,search=name,key="server")
    if isinstance(server,bool) or server == None:
        pass
    else:
        channel = server["channels"]
        server = server["server"]
    return templates.TemplateResponse("server.html",{"request":request,"server":server,"channels":channel,"image":request.cookies.get("image")})

@app.post("/webhook")#githubappsに登録されたら飛ばされるサイト
async def webhook(request: Request):
    return RedirectResponse("serverlist")

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()#websocketの確立を待つ
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            await connection.send_json(message)


manager = ConnectionManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)#websocketの確立を待つ
    while True:
        try:
            data = await websocket.receive_json()#messageの受信開始
            match data["data"]:
                case "makeserver":
                    try:
                        user_rec = kit.supabase.searchread(table=serverdata, search=websocket.cookies.get("node_id"), key="username")
                        user_servers = []
                        if user_rec not in (None, False) and isinstance(user_rec, dict):
                            sv = user_rec.get("servers") or ""
                            user_servers = [s for s in sv.split("|") if s]

                        # 正確な一致で存在チェック
                        if data["servername"] in user_servers:
                            await websocket.send_json({"response": False})
                            break

                        # 作成可能
                        await websocket.send_json({"response": True, "data": data["servername"]})
                        if not user_rec:
                            kit.supabase.newdata(table=serverdata, data=websocket.cookies.get("node_id"), column="username")
                            servers_data = data["servername"]
                        else:
                            servers_data = (user_rec.get("servers") or "")
                            servers_data = servers_data + ('|' if servers_data else '') + data["servername"]
                        kit.supabase.update(table=serverdata, data=servers_data, column="servers", overwrite=False, former=websocket.cookies.get("node_id"), columneq="username")
                        #メンバーリスト作成
                        kit.supabase.newdata(table=memberlist, data=data["servername"], column="server")
                        kit.supabase.update(table=memberlist, data=websocket.cookies.get("node_id"), column="username", columneq="server", overwrite=None, former=data["servername"])
                        #チャンネルリストに追加
                        kit.supabase.newdata(table=channeldata, data=data["servername"], column="server")
                        kit.supabase.update(table=channeldata, data="general|announcements|resources", column="channels", columneq="server", overwrite=None, former=data["servername"])
                        await manager.broadcast({"event": "new_server", "data": data["servername"]})
                        if data["kinds"] == "public":
                            kit.supabase.newdata(table=openchat, data=data["servername"], column="server")
                        else:
                            pass
                    except Exception as e:
                        kit.supabase.newdata(table=serverdata,data=websocket.cookies.get("node_id"),column="username")
                        if kit.supabase.searchread(table=serverdata,search=websocket.cookies.get("node_id"),key="username")["servers"] != None:
                            servers_data = str(kit.supabase.searchread(table=serverdata,search=websocket.cookies.get("node_id"),key="username")["servers"]) + '|' + data["servername"]
                        else:
                            servers_data = data["servername"]
                        kit.supabase.update(table=serverdata,data=servers_data,column="servers",overwrite=False,former=websocket.cookies.get("node_id"),columneq="username")
                        kit.supabase.newdata(table=channeldata,data=data["servername"],column="server")
                        kit.supabase.update(table=channeldata, data="general|announcements|resources", column="channels", columneq="server", overwrite=None, former=data["servername"])
                        await websocket.send_json({"response":True,"data":data["servername"]})
                        await manager.broadcast({"event":"new_server","data":data["servername"]})
                        if data["kinds"] == "public":
                            kit.supabase.newdata(table=openchat,data=data["servername"],column="server")
                case "chatdata":
                    cheak,token,datas,avatar_url = await get_jwt()
                    if cheak == True:
                        database_filedata = kit.github.read(token=token,filepass=f"{data['server']}_{data['channel']}.txt",repo_name=websocket.cookies.get("repo"))#githubに保存されているmessage送信
                        if type(database_filedata) != bool:
                            database_filedata = database_filedata["content"].split("|")
                            database_filedata = database_filedata[-20:]
                            if database_filedata != False:
                                await websocket.send_json({"data":"message","message":database_filedata})
                        else:
                            kit.github.createfile(token=token,repo_name=websocket.cookies.get("repo"),update_data="",filepass=f"{data['server']}_{data['channel']}.txt")
                            await websocket.send_json({"data":"message"})
                        cheak,repos,avatar_url = await savemessage(websocket.cookies.get("node_id"))#databaseのdataをsupabaseに移行
                case "oldmessage":
                    cheak,token,datas,avatar_url = await get_jwt()
                    if cheak == True:
                        database_filedata = kit.github.read(token=token,filepass=f"{data['server']}_{data['channel']}.txt",repo_name=websocket.cookies.get("repo"))#githubに保存されているmessage送信
                        database_filedata = database_filedata["content"].split("|")
                        database_filedata = database_filedata[-40:-20]
                        await websocket.send_json({"data":"message","message":database_filedata})
                case "message":
                    if "|" not in data["message"]:
                        match data:
                            case {"message": msg} if isinstance(msg, str) and "/join" in msg:
                                    node_id = data["message"].replace("/join ","")
                                    print(msg)
                                    kit.supabase.update(table=memberlist, data=f"{kit.supabase.searchread(table=memberlist,search=data["server"],key="server")["username"]}|{node_id}", column="username", columneq="server", overwrite=None, former=data["server"])
                            case _:
                                usernames = kit.supabase.searchread(table=memberlist,search=websocket.cookies.get("node_id"),key="username")
                                if not isinstance(usernames,bool):
                                    usernames = usernames["username"]
                                    usernames = usernames.split("|")
                                    print(usernames)
                                else:
                                    usernames = [websocket.cookies.get("node_id")]
                                for username in usernames:
                                    if not kit.supabase.searchread(table=messagedata, search=data["channel"], key="channel"):
                                        kit.supabase.newdata(table=messagedata, data=data["server"], column="server")

                                        first_message = f"{websocket.cookies.get('image').replace('|','')}|{websocket.cookies.get('username')}:{data['message']}"
                                        kit.supabase.update(
                                            table=messagedata,
                                            data=first_message,
                                            former=data["server"],
                                            columneq="server",
                                            column="message",
                                            overwrite=False
                                        )

                                        kit.supabase.update(
                                            table=messagedata,
                                            data=data["channel"],
                                            former=data["server"],
                                            columneq="server",
                                            column="channel",
                                            overwrite=False
                                        )

                                        kit.supabase.update(
                                            table=messagedata,
                                            data=username,
                                            former=data["server"],
                                            columneq="server",
                                            column="username",
                                            overwrite=False
                                        )

                                    else:
                                        existing = kit.supabase.searchread(
                                            table=messagedata,
                                            search=data["server"],
                                            key="server"
                                        )["message"]

                                        newmsg = f"{existing}|{websocket.cookies.get('username')}:{data['message']}"

                                        kit.supabase.update(
                                            table=messagedata,
                                            data=newmsg,
                                            former=data["server"],      # ← これが正しい
                                            columneq="server",          # ← これも合わせる
                                            column="message",
                                            overwrite=False
                                        )


                        image_used = (websocket.cookies.get("image") or "").replace("|", "")
                        username_used = websocket.cookies.get("username") or "unknown"
                        broadcast_payload = {
                            "data": "addmessage",
                            "server": data.get("server"),
                            "channel": data.get("channel"),
                            "image": image_used,
                            "username": username_used,
                            "message": data.get("message")
                        }
                        await manager.broadcast(broadcast_payload)
                case "addchannel":
                    await websocket.send_text(data["server"])
                    kit.supabase.update(table=channeldata,data=f"{kit.supabase.searchread(table=channeldata,search=data["server"],key="server")["channels"]}|{data["channel"]}",former=data["server"],columneq="server",column="channels",overwrite=False)
                case "joinserver":
                    # 参加可否判定:
                    # - openchat に server が存在すれば公開サーバーで参加可能
                    # - あるいはユーザー自身の server リストに対象サーバー名が含まれていれば参加許可（プライベートサーバー）
                    user_rec = kit.supabase.searchread(table=serverdata, search=websocket.cookies.get("node_id"), key="username")
                    user_has_server = False
                    if user_rec not in (None, False):
                        user_servers = user_rec.get("servers") or ""
                        user_has_server = data["server"] in user_servers.split("|") if user_servers else False

                    r = kit.supabase.searchread(table=openchat, search=data["server"], key="server")
                    is_public = (r not in (None, False) and r.get("server") is not None)

                    if user_rec is not False and (is_public or user_has_server):
                        # ユーザーの server 列に参加サーバーを追加
                        current_servers = user_rec.get("servers") if isinstance(user_rec, dict) else None
                        if current_servers:
                            new_servers = f"{current_servers}|{data['server']}" if data['server'] not in current_servers.split("|") else current_servers
                        else:
                            new_servers = data['server']

                        kit.supabase.update(table=serverdata, data=new_servers, former=websocket.cookies.get("node_id"), columneq="username", column="servers", overwrite=False)
                        # memberlist に参加者を追加（既存の形式を維持）
                        try:
                            existing_usernames = kit.supabase.searchread(table=memberlist, search=data["server"], key="server")
                            if existing_usernames and isinstance(existing_usernames, dict):
                                members_str = existing_usernames.get("username") or ""
                                if websocket.cookies.get("node_id") not in members_str.split("|"):
                                    new_members = f"{members_str}|{websocket.cookies.get('node_id')}" if members_str else websocket.cookies.get('node_id')
                                else:
                                    new_members = members_str
                            else:
                                new_members = websocket.cookies.get('node_id')
                        except Exception:
                            new_members = websocket.cookies.get('node_id')

                        kit.supabase.update(table=memberlist, data=new_members, former=data["server"], columneq="server", column="username", overwrite=None)
                        await websocket.send_text(True)


        except WebSocketDisconnect:
            manager.disconnect(websocket)
            await manager.broadcast({"event":"disconnect","node_id":websocket.cookies.get("node_id")})
        except RuntimeError:
            raise Websocketerror("強制的に切断されました")
        except Exception as e:
            raise Websocketerror(e)

app.include_router(router)
uvicorn.run(app,log_level="debug")