let serverdata = document.querySelector('p');
let serverText = ""; // 追加

if (serverdata) {
  serverText = serverdata.textContent;
} else {
  console.error("段落要素が見つかりませんでした (タグ: 'p')");
}

let serverlist = serverText.split('|');
console.log(serverlist);
if (serverlist[0] !== "False") {
  const serverContainer = document.getElementById("server");
  if (serverContainer) {
    for (const serverName of serverlist) {
      const container = document.createElement("div");
      container.className = "contents";

      const h3 = document.createElement("h3");
      h3.className = serverName;
      h3.textContent = serverName;

      const button = document.createElement("button");
      button.className = "btn-style4 size-medium width-auto radius-medium";
      button.textContent = "参加";
      button.addEventListener("click", () => joinServer(serverName));

      container.appendChild(h3);
      container.appendChild(button);
      serverContainer.appendChild(container);
    }
  } else {
    console.error("#server 要素が見つかりませんでした");
  }
}

function joinServer(name) {
  console.log("参加するサーバー:", name);
  location.href = "/server/?name=" + encodeURIComponent(name);
}
