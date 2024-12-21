export async function onRequest({ request, env, params }) {
  const { pathname } = new URL(request.url);
  const path = pathname === "/" ? "" : pathname;

  // 获取目录内容
  const files = await env.ASSETS.list({ prefix: path.slice(1) });

  // 构建 HTML
  const html = `
    <!DOCTYPE html>
    <html>
    <head>
      <title>Directory: ${pathname}</title>
      <style>
        body { font-family: system-ui; max-width: 800px; margin: 0 auto; padding: 20px; }
        .item { padding: 10px; border-bottom: 1px solid #eee; }
        .item:hover { background: #f5f5f5; }
        a { color: #0051c3; text-decoration: none; }
        .size { color: #666; float: right; }
      </style>
    </head>
    <body>
      <h2>Index of ${pathname}</h2>
      ${
        pathname !== "/"
          ? `<div class="item"><a href="${new URL(
              "..",
              request.url
            )}">..</a></div>`
          : ""
      }
      ${files.objects
        .map((file) => {
          const name = file.key.split("/").pop() || file.key;
          const isDir = file.key.endsWith("/");
          return `
          <div class="item">
            <a href="${new URL(name + (isDir ? "/" : ""), request.url)}">
              ${name}${isDir ? "/" : ""}
            </a>
            ${
              !isDir ? `<span class="size">${formatSize(file.size)}</span>` : ""
            }
          </div>
        `;
        })
        .join("\n")}
    </body>
    </html>
  `;

  return new Response(html, {
    headers: { "content-type": "text/html;charset=UTF-8" },
  });
}

function formatSize(bytes) {
  if (bytes === 0) return "0 B";
  const k = 1024;
  const sizes = ["B", "KB", "MB", "GB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return `${(bytes / Math.pow(k, i)).toFixed(1)} ${sizes[i]}`;
}
