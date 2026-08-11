"""
dashboard.py
------------
Stitches the four individual Gold-layer charts into a single 2x2
"Gold Layer -- Business Analytics Dashboard" image, the way a BI tool
(Power BI / Tableau canvas) would present them together.
"""

import matplotlib.image as mpimg
import matplotlib.pyplot as plt


def build_dashboard(gold_dir: str, outpath: str):
    files = [
        (f"{gold_dir}/chart_total_spend_by_customer.png", "Total Spend by Customer"),
        (f"{gold_dir}/chart_transaction_distribution.png", "Transaction Distribution by Spend Category"),
        (f"{gold_dir}/chart_total_vs_avg_by_category.png", "Total vs Avg Amount by Spend Category"),
        (f"{gold_dir}/chart_avg_spend_per_customer.png", "Avg Spend per Customer (Ranked)"),
    ]

    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle("Gold Layer \u2014 Business Analytics Dashboard", fontsize=18, fontweight="bold")

    for ax, (path, _title) in zip(axes.flat, files):
        img = mpimg.imread(path)
        ax.imshow(img)
        ax.axis("off")

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.savefig(outpath, dpi=150)
    plt.close(fig)
    print(f"[GOLD] Combined dashboard saved -> {outpath}")


if __name__ == "__main__":
    build_dashboard("gold", "gold/gold_layer_dashboard.png")
