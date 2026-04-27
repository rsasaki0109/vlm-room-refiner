import { test } from "@playwright/test";
import path from "path";

test("capture real UI screenshot (mocked API)", async ({ page }) => {
  // Mock backend so Ollama is not required.
  await page.route("**/analyze", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json; charset=utf-8",
      body: JSON.stringify(
        {
          room_type: "ワンルーム",
          style: "無印系ミニマル",
          problems: [
            "配線が床沿いに見え、生活感が出やすい",
            "収納が足りず、床に物が溜まりやすい",
            "照明が単一で陰影が弱い",
          ],
          recommendations: [
            "配線モールで壁沿いにまとめ、床の露出配線を減らす",
            "縦長ラック（幅60cm前後）を壁際に置き、床置き物を集約",
            "間接照明を1灯追加し、色温度を暖色寄りに統一",
          ],
          shopping_keywords: [
            "配線モール 白 粘着",
            "スチールラック 幅60 奥行30",
            "フロアライト 間接照明 調光 暖色",
          ],
        },
        null,
        2
      ),
    });
  });

  await page.goto("/");

  const sample = path.join(
    process.cwd(),
    "docs",
    "assets",
    "sample-room.svg"
  );
  await page.setInputFiles('input[type="file"]', sample);

  // Select preset (optional)
  await page.getByRole("button", { name: "韓国風" }).click();

  await page.getByPlaceholder("例: 韓国風 / ミニマル").fill("ミニマル");
  await page.getByPlaceholder("例: 1万円前後").fill("〜1万円");
  await page
    .getByText("Before/After 的な文言を積極的に入れる")
    .click();
  await page.getByRole("button", { name: "分析する" }).click();

  // Wait until JSON shows up.
  await page.locator("#demo").getByText('"room_type":').first().waitFor();

  await page.screenshot({
    path: path.join(process.cwd(), "docs", "assets", "screenshot.png"),
    fullPage: true,
  });
});

