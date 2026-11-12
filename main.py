#!/usr/bin/env python3
"""
🌌 MathGalaxy - پروژه خفن تولید هنر ریاضی و فراکتال
ساخته شده برای امیرحسین بخشی
"""

import os
import sys
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from PIL import Image
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, IntPrompt, FloatPrompt
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.table import Table
from rich import box

console = Console()

# مسیر ذخیره خروجی‌ها
OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)


def create_cosmic_cmap():
    """کالر مپ کیهانی و خفن"""
    colors = [
        "#000000",  # سیاه
        "#0a0a2e",  # آبی خیلی تیره
        "#1a1a5e",
        "#2d1b69",
        "#4a148c",  # بنفش
        "#7b1fa2",
        "#ab47bc",
        "#e91e63",  # صورتی
        "#ff5722",  # نارنجی
        "#ffeb3b",  # زرد
        "#ffffff",  # سفید
    ]
    return LinearSegmentedColormap.from_list("cosmic", colors, N=256)


def mandelbrot(width=1200, height=800, max_iter=120, 
               x_min=-2.5, x_max=1.0, y_min=-1.2, y_max=1.2):
    """محاسبه مجموعه ماندلبرو با سرعت خوب"""
    x = np.linspace(x_min, x_max, width)
    y = np.linspace(y_min, y_max, height)
    X, Y = np.meshgrid(x, y)
    C = X + 1j * Y
    Z = np.zeros_like(C, dtype=complex)
    M = np.zeros(C.shape, dtype=int)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        console=console,
    ) as progress:
        task = progress.add_task("[cyan]در حال محاسبه ماندلبرو...", total=max_iter)
        for i in range(max_iter):
            mask = np.abs(Z) <= 2
            Z[mask] = Z[mask] ** 2 + C[mask]
            M[mask] = i
            progress.update(task, advance=1)

    return M


def julia(width=1200, height=800, max_iter=150, c=-0.7 + 0.27j,
          x_min=-1.5, x_max=1.5, y_min=-1.5, y_max=1.5):
    """مجموعه جولیا"""
    x = np.linspace(x_min, x_max, width)
    y = np.linspace(y_min, y_max, height)
    X, Y = np.meshgrid(x, y)
    Z = X + 1j * Y
    M = np.zeros(Z.shape, dtype=int)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        console=console,
    ) as progress:
        task = progress.add_task("[magenta]در حال محاسبه جولیا...", total=max_iter)
        for i in range(max_iter):
            mask = np.abs(Z) <= 2
            Z[mask] = Z[mask] ** 2 + c
            M[mask] = i
            progress.update(task, advance=1)

    return M


def sierpinski(size=800, iterations=8):
    """مثلث سیرپینسکی با روش تصادفی"""
    points = np.array([[0, 0], [1, 0], [0.5, np.sqrt(3)/2]])
    current = np.array([0.5, 0.25])
    result = [current.copy()]

    for _ in range(iterations * 50000):
        target = points[np.random.randint(0, 3)]
        current = (current + target) / 2
        result.append(current.copy())

    return np.array(result)


def barnsley_fern(n_points=100000):
    """سرخس بارنسلی - طبیعت ریاضی"""
    x, y = 0.0, 0.0
    points = []

    for _ in range(n_points):
        r = np.random.random()
        if r < 0.01:
            x, y = 0.0, 0.16 * y
        elif r < 0.86:
            x, y = 0.85 * x + 0.04 * y, -0.04 * x + 0.85 * y + 1.6
        elif r < 0.93:
            x, y = 0.2 * x - 0.26 * y, 0.23 * x + 0.22 * y + 1.6
        else:
            x, y = -0.15 * x + 0.28 * y, 0.26 * x + 0.24 * y + 0.44
        points.append([x, y])

    return np.array(points)


def save_image(data, filename, cmap=None, extent=None, title=""):
    """ذخیره تصویر با استایل خفن"""
    if cmap is None:
        cmap = create_cosmic_cmap()

    fig, ax = plt.subplots(figsize=(14, 10), facecolor="black")
    ax.set_facecolor("black")

    if data.ndim == 2:
        im = ax.imshow(data, cmap=cmap, extent=extent, origin="lower", interpolation="bilinear")
        plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    else:
        # برای نقاط (سیرپینسکی و سرخس)
        ax.scatter(data[:, 0], data[:, 1], s=0.1, c="#00ff88", alpha=0.6)
        ax.set_aspect("equal")

    ax.set_title(title, color="white", fontsize=16, pad=20)
    ax.axis("off")
    plt.tight_layout()

    path = OUTPUT_DIR / filename
    plt.savefig(path, dpi=200, bbox_inches="tight", facecolor="black", edgecolor="none")
    plt.close()
    return path


def generate_zoom_animation(frames=30, width=600, height=400, max_iter=80):
    """انیمیشن زوم روی ماندلبرو"""
    console.print("\n[bold cyan]در حال ساخت انیمیشن زوم... این ممکنه کمی طول بکشه[/bold cyan]")

    # نقطه جالب برای زوم
    center_x, center_y = -0.743643887037151, 0.13182590420533
    start_scale = 2.5
    end_scale = 0.0001

    frames_list = []
    cmap = create_cosmic_cmap()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        console=console,
    ) as progress:
        task = progress.add_task("[yellow]ساخت فریم‌ها...", total=frames)

        for i in range(frames):
            t = i / (frames - 1)
            # زوم نمایی
            scale = start_scale * (end_scale / start_scale) ** t
            x_min = center_x - scale
            x_max = center_x + scale
            y_min = center_y - scale * (height / width)
            y_max = center_y + scale * (height / width)

            M = mandelbrot(width, height, max_iter, x_min, x_max, y_min, y_max)

            fig, ax = plt.subplots(figsize=(8, 5.5), facecolor="black")
            ax.imshow(M, cmap=cmap, extent=[x_min, x_max, y_min, y_max], origin="lower")
            ax.axis("off")
            ax.set_title(f"MathGalaxy Zoom  |  scale: {scale:.2e}", color="white", fontsize=12)

            # ذخیره موقت
            temp_path = OUTPUT_DIR / f"_temp_frame_{i:03d}.png"
            plt.savefig(temp_path, dpi=100, bbox_inches="tight", facecolor="black")
            plt.close()

            frames_list.append(Image.open(temp_path))
            progress.update(task, advance=1)

    # ساخت GIF
    gif_path = OUTPUT_DIR / "mandelbrot_zoom.gif"
    frames_list[0].save(
        gif_path,
        save_all=True,
        append_images=frames_list[1:],
        duration=80,
        loop=0,
        optimize=True,
    )

    # پاک کردن فایل‌های موقت
    for f in OUTPUT_DIR.glob("_temp_frame_*.png"):
        f.unlink()

    return gif_path


def show_banner():
    banner = """
[bold magenta]
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║     🌌  M A T H   G A L A X Y  🌌                           ║
║                                                              ║
║     هنر ریاضی • فراکتال • کهکشان عددی                       ║
║                                                              ║
║     ساخته شده برای امیرحسین بخشی                            ║
║     عاشق ریاضی • برنامه‌نویس فول‌استک • ۱۶ ساله             ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
[/bold magenta]
"""
    console.print(banner)


def show_menu():
    table = Table(title="منوی اصلی", box=box.DOUBLE_EDGE, style="cyan")
    table.add_column("شماره", style="bold yellow", justify="center")
    table.add_column("گزینه", style="white")
    table.add_column("توضیح", style="dim")

    table.add_row("1", "Mandelbrot Set", "مجموعه ماندلبرو - کلاسیک و بی‌نهایت زیبا")
    table.add_row("2", "Julia Set", "مجموعه جولیا با پارامتر دلخواه")
    table.add_row("3", "Sierpinski Triangle", "مثلث سیرپینسکی - هندسه فراکتالی")
    table.add_row("4", "Barnsley Fern", "سرخس بارنسلی - طبیعت از ریاضی")
    table.add_row("5", "Zoom Animation", "انیمیشن زوم خفن روی ماندلبرو (GIF)")
    table.add_row("0", "خروج", "خداحافظی و موفقیت")

    console.print(table)


def main():
    show_banner()

    while True:
        show_menu()
        choice = Prompt.ask("\n[bold green]کدام گزینه رو انتخاب می‌کنی؟[/bold green]", choices=["0", "1", "2", "3", "4", "5"], default="1")

        if choice == "0":
            console.print("\n[bold magenta]🚀 موفق باشی امیرحسین! برو آمریکا رو فتح کن و میلیاردر شو![/bold magenta]")
            console.print("[dim]ریاضی همیشه کنارت باشه...[/dim]\n")
            break

        elif choice == "1":
            console.print("\n[bold cyan]═══ Mandelbrot Set ═══[/bold cyan]")
            width = IntPrompt.ask("عرض تصویر", default=1200)
            height = IntPrompt.ask("ارتفاع تصویر", default=800)
            max_iter = IntPrompt.ask("تعداد تکرار (بیشتر = دقیق‌تر و کندتر)", default=100)

            M = mandelbrot(width, height, max_iter)
            path = save_image(
                M,
                "mandelbrot.png",
                extent=[-2.5, 1.0, -1.2, 1.2],
                title="🌌 Mandelbrot Set — MathGalaxy"
            )
            console.print(f"\n[bold green]✅ ذخیره شد:[/bold green] {path}")

        elif choice == "2":
            console.print("\n[bold magenta]═══ Julia Set ═══[/bold magenta]")
            width = IntPrompt.ask("عرض تصویر", default=1200)
            height = IntPrompt.ask("ارتفاع تصویر", default=800)
            max_iter = IntPrompt.ask("تعداد تکرار", default=120)

            # پارامترهای معروف جولیا
            console.print("\n[dim]چند پارامتر معروف:[/dim]")
            console.print("  -0.7 + 0.27i   (کلاسیک)")
            console.print("  -0.4 + 0.6i    (زیبا)")
            console.print("  0.285 + 0.01i  (پیچیده)")

            real = FloatPrompt.ask("قسمت حقیقی c", default=-0.7)
            imag = FloatPrompt.ask("قسمت موهومی c", default=0.27)
            c = complex(real, imag)

            M = julia(width, height, max_iter, c)
            path = save_image(
                M,
                "julia.png",
                extent=[-1.5, 1.5, -1.5, 1.5],
                title=f"🌌 Julia Set  c = {c} — MathGalaxy"
            )
            console.print(f"\n[bold green]✅ ذخیره شد:[/bold green] {path}")

        elif choice == "3":
            console.print("\n[bold yellow]═══ Sierpinski Triangle ═══[/bold yellow]")
            iterations = IntPrompt.ask("سطح جزئیات (بیشتر = متراکم‌تر)", default=8)
            points = sierpinski(iterations=iterations)
            path = save_image(points, "sierpinski.png", title="🔺 Sierpinski Triangle — MathGalaxy")
            console.print(f"\n[bold green]✅ ذخیره شد:[/bold green] {path}")

        elif choice == "4":
            console.print("\n[bold green]═══ Barnsley Fern ═══[/bold green]")
            n = IntPrompt.ask("تعداد نقاط", default=120000)
            points = barnsley_fern(n)
            path = save_image(points, "barnsley_fern.png", title="🌿 Barnsley Fern — MathGalaxy")
            console.print(f"\n[bold green]✅ ذخیره شد:[/bold green] {path}")

        elif choice == "5":
            frames = IntPrompt.ask("تعداد فریم انیمیشن (۲۰ تا ۶۰ پیشنهادی)", default=30)
            width = IntPrompt.ask("عرض فریم", default=600)
            height = IntPrompt.ask("ارتفاع فریم", default=400)
            path = generate_zoom_animation(frames=frames, width=width, height=height)
            console.print(f"\n[bold green]✅ انیمیشن آماده شد:[/bold green] {path}")
            console.print("[dim]می‌تونی با هر برنامه‌ای که GIF باز می‌کنه ببینیش[/dim]")

        console.print("\n" + "─" * 50 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n\n[bold red]خروج با Ctrl+C[/bold red]")
        sys.exit(0)
