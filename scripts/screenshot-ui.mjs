import { spawn } from "node:child_process";

function run(cmd, args, opts = {}) {
  return new Promise((resolve, reject) => {
    const p = spawn(cmd, args, { stdio: "inherit", shell: false, ...opts });
    p.on("exit", (code) => {
      if (code === 0) resolve();
      else reject(new Error(`${cmd} exited with ${code}`));
    });
  });
}

async function main() {
  // Ensure deps are installed before running this.
  await run("npx", ["-y", "playwright", "install", "chromium"]);
  await run("npx", ["-y", "playwright", "test", "e2e/screenshot.spec.ts"]);
  console.log("Wrote docs/assets/screenshot.png");
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});

