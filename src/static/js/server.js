// =========================
// 初期値
// =========================
let currentChannel = null;

// 隠しフィールドからデータ取得
const channelString = document.getElementById("channels").textContent;
const channels = channelString.split("|");

const serverName = document.getElementById("server").textContent;

// =========================
// WebSocket（1つだけ使う）
// =========================
const socket = new WebSocket("wss:devlinkhub.net/ws");

socket.onmessage = (event) => {
    // JSON 形式のペイロードを受け取る
    const payload = JSON.parse(event.data);
    console.log('ws receive:', payload);

    if (payload.data === "message") {
        // 履歴メッセージ（既存の配列フォーマット）
        $("#glasschat").empty();
        const arr = payload.message;
        if (!Array.isArray(arr)) return;
        for (let i = 0; i < arr.length; i += 2) {
            if (!arr[i + 1]) continue;
            $("#glasschat").append(`
                <div id="chatcard" style="display:flex;">
                    <img src="${arr[i]}" style="height:50px; width:auto;">
                    <p>${arr[i + 1]}</p>
                </div>
            `);
        }
        return;
    }

    if (payload.data === "addmessage") {
        // リアルタイム受信（構造化ペイロード）
        const img = payload.image || '';
        const user = payload.username || 'unknown';
        const msg = payload.message || '';
        $("#glasschat").append(`
            <div id="chatcard" style="display:flex;">
                <img src="${img}" style="height:50px; width:auto;">
                <p>${user}: ${msg}</p>
            </div>
        `);
        return;
    }
};


    // =========================
    // チャンネル一覧を表示
    // =========================
    for (const ch of channels) {
        $("#channel").append(`
                <button onclick="load_channel('${ch}')"class="btn-style4 size-medium width-auto radius-medium">${ch}</button>
        `);
}

// =========================
// チャンネル読み込み
// =========================
function load_channel(channel) {
    let now_channel = document.getElementById('now_channel').textContent; //宣言
    document.getElementById('now_channel').textContent = channel;
    currentChannel = channel;

    const payload = {
        data: "chatdata",
        server: serverName,
        channel: channel
    };

    console.log("チャットデータ要求:", payload);

    socket.send(JSON.stringify(payload));
}

// =========================
// メッセージ送信
// =========================
function sendMessage() {
    if (!currentChannel) {
        console.warn("チャンネルが選択されていません");
        return;
    }

    const form = document.getElementById("message");
    const msg = form.value
    if (!msg) return;

    const payload = {
        data: "message",
        message: msg.trim(),
        server: serverName,
        channel: currentChannel
    };

    // クライアント側で保持している avatar URL を明示的に送る
    const imageElem = document.getElementById("image");
    if (imageElem) {
        payload.image = imageElem.textContent || imageElem.value || null;
    }

    form.value = ""
    console.log("送信データ:", payload);
    socket.send(JSON.stringify(payload));
}

let lastEnterTime = 0; // 前回Enter押下時刻

document.getElementById("message").addEventListener("keydown", (e) => {
    if (e.key === "Enter") {
        const now = Date.now();
        if (now - lastEnterTime < 500) { // 500ms以内に2回目のEnter
            e.preventDefault();  // フォーム送信や改行を防ぐ
            sendMessage();       // メッセージ送信
            lastEnterTime = 0;   // リセット
        } else {
            lastEnterTime = now; // 今回のEnter押下時間を保存
        }
    }
});
