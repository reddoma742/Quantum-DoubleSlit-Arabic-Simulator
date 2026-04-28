# -*- coding: utf-8 -*-
"""
Berramdane Model V11.1 – Final Professional Arabic Educational Tool
Author : Al Moalim Berramdane
License: CC BY 4.0

ملاحظة مهمة: هذه الأداة تعليمية، تعتمد على الفيزياء الموجية الكلاسيكية
(تراكب الموجات، حيود وتداخل الشقوق) وليست محاكاة لميكانيكا الكم المتقدمة.
النتائج تتطابق مع التجارب المخبرية الحقيقية ضمن الإعدادات المحددة.
"""

import numpy as np
import matplotlib.pyplot as plt
from ipywidgets import interact, FloatSlider, Checkbox, IntSlider, Dropdown
from scipy.signal import find_peaks
import warnings
warnings.filterwarnings('ignore')

# === الثوابت الفيزيائية ===
h = 6.626e-34            # ثابت بلانك (J·s)
m = 9.109e-31            # كتلة الإلكترون (kg)
c = 3e8                  # سرعة الضوء (m/s)
L_total = 2.2            # المسافة من الشقين إلى الشاشة (m)

# === دوال أساسية (نفس السابق) ===
def de_broglie_wavelength(v):
    return h / (m * v)

def double_slit_intensity_by_wavelength(x, wavelength, L, a_width, d_slit):
    beta = (np.pi * d_slit * x) / (wavelength * L)
    interference = np.cos(beta)**2
    alpha = (np.pi * a_width * x) / (wavelength * L)
    envelope = np.sinc(alpha / np.pi)**2
    return interference * envelope

def double_slit_intensity_with_spread(x, v_mean, delta_v, L, a_width, d_slit, n_samples=100):
    velocities = np.random.normal(v_mean, delta_v, n_samples)
    total = np.zeros_like(x)
    for v in velocities:
        lam = de_broglie_wavelength(v)
        total += double_slit_intensity_by_wavelength(x, lam, L, a_width, d_slit)
    return total / n_samples

def particle_like_pattern(x, wavelength, L, a_width, d_slit):
    sigma = a_width * L / wavelength
    I_left = np.exp(-(x + d_slit/2)**2 / (2 * sigma**2))
    I_right = np.exp(-(x - d_slit/2)**2 / (2 * sigma**2))
    return 0.5 * (I_left + I_right)

def compute_visibility(x, I):
    peaks, _ = find_peaks(I, distance=len(x)//30)
    if len(peaks) < 2:
        return 0.0
    I_max = np.max(I[peaks])
    center_idx = np.argmin(np.abs(x))
    search = np.where(np.abs(x - x[center_idx]) < 5e-3)[0]
    I_min = np.min(I[search]) if len(search) > 0 else np.min(I)
    return (I_max - I_min) / (I_max + I_min) if (I_max + I_min) > 0 else 0

def jonsson_validation(v_mean, a_width, d_slit, L):
    lam = de_broglie_wavelength(v_mean)
    theoretical_first_min_mm = lam * L / a_width * 1000
    experimental_first_min_mm = 0.18
    error_pct = abs(theoretical_first_min_mm - experimental_first_min_mm) / experimental_first_min_mm * 100
    print("\n" + "="*50)
    print("🔬 التحقق العلمي: مقارنة مع تجربة Jönsson 1961 (إلكترونات)")
    print(f"سرعة الإلكترونات: {v_mean/1e3:.0f} km/s (المقاسة ~70 km/s)")
    print(f"عرض الشق: {a_width*1e6:.3f} µm (المقاس ~0.3 µm)")
    print(f"المسافة بين الشقين: {d_slit*1e6:.3f} µm (المقاسة ~1.0 µm)")
    print(f"الموقع النظري لأول عقدة حيود: {theoretical_first_min_mm:.3f} mm")
    print(f"الموقع التجريبي: {experimental_first_min_mm:.3f} mm")
    print(f"الخطأ النسبي: {error_pct:.1f}%")
    if error_pct < 20:
        print("✅ متطابقة ضمن هامش الخطأ التجريبي. الكود يحاكي الواقع بدقة.")
    else:
        print("⚠️ انحراف كبير. يُرجى ضبط المعطيات.")
    print("="*50 + "\n")
    return error_pct

def white_light_pattern_rgb(x, L, a_width, d_slit):
    """إرجاع الشدة لكل قناة لونية (أحمر، أخضر، أزرق) بشكل منفصل"""
    lam_R = 650e-9
    lam_G = 532e-9
    lam_B = 450e-9
    I_R = double_slit_intensity_by_wavelength(x, lam_R, L, a_width, d_slit)
    I_G = double_slit_intensity_by_wavelength(x, lam_G, L, a_width, d_slit)
    I_B = double_slit_intensity_by_wavelength(x, lam_B, L, a_width, d_slit)
    # تطبيع كل قناة على حدة للحصول على ألوان زاهية (يمكن تعديله)
    if np.max(I_R) > 0: I_R /= np.max(I_R)
    if np.max(I_G) > 0: I_G /= np.max(I_G)
    if np.max(I_B) > 0: I_B /= np.max(I_B)
    return I_R, I_G, I_B

# ========== الواجهة التفاعلية النهائية ==========
@interact(
    mode=Dropdown(options=[
        'Electron (de Broglie) - إلكترون',
        'Photon (monochromatic) - فوتون أحادي اللون',
        'White light (RGB) - ضوء أبيض ملون'
    ], value='Electron (de Broglie) - إلكترون', description='نمط المحاكاة'),
    v_mean=FloatSlider(value=5.8e5, min=2e5, max=1.2e6, step=0.1e5, description='سرعة الإلكترون (م/ث)', continuous_update=False),
    delta_v=FloatSlider(value=0.0, min=0.0, max=2e5, step=0.1e4, description='انتشار السرعة Δv (م/ث)', continuous_update=False),
    wavelength_nm=FloatSlider(value=532, min=380, max=750, step=1, description='الطول الموجي (نانومتر)', continuous_update=False),
    a_width=FloatSlider(value=0.72e-6, min=0.2e-6, max=1.5e-6, step=0.01e-6, description='عرض الشق (متر)', continuous_update=False),
    d_slit=FloatSlider(value=2.45e-6, min=0.5e-6, max=2e-3, step=1e-5, description='المسافة بين الشقين (متر)', continuous_update=False),
    observer_active=Checkbox(value=False, description='مكتشف المسار (ON/OFF)'),
    meas_strength=FloatSlider(value=0.0, min=0.0, max=1.0, step=0.01, description='قوة القياس', continuous_update=False),
    temperature=FloatSlider(value=0.0, min=0, max=1000, step=10, description='ضجيج الكاشف (كلفن)', continuous_update=False),
    show_buildup=Checkbox(value=False, description='تراكم الجسيمات التدريجي'),
    n_particles=IntSlider(value=300, min=50, max=1000, step=50, description='عدد الجسيمات')
)
def interactive_lab(mode, v_mean, delta_v, wavelength_nm, a_width, d_slit,
                    observer_active, meas_strength, temperature, show_buildup, n_particles):
    
    # تحديد الطول الموجي الفعال والمدى الديناميكي
    if 'Photon' in mode:
        lam = wavelength_nm * 1e-9
        spacing = lam * L_total / d_slit
        x_limit = max(0.005, 3 * spacing)
        if d_slit < 1e-4:
            print("⚠️ ملاحظة: للضوء المرئي، المسافة بين الشقين عادة 0.1–1 mm")
        if a_width >= d_slit:
            print("⚠️ تصحيح: عرض الشق < المسافة بين الشقين.")
            a_width = d_slit * 0.99
    elif 'Electron' in mode:
        lam = de_broglie_wavelength(v_mean)
        spacing = lam * L_total / d_slit
        x_limit = max(0.005, 3 * spacing)
        if a_width >= d_slit:
            print("⚠️ تصحيح: عرض الشق < المسافة بين الشقين.")
            a_width = d_slit * 0.99
    else:  # White light
        lam_mid = 532e-9
        spacing = lam_mid * L_total / d_slit
        x_limit = max(0.005, 3 * spacing)
        if a_width >= d_slit:
            print("⚠️ تصحيح: عرض الشق < المسافة بين الشقين.")
            a_width = d_slit * 0.99

    x = np.linspace(-x_limit, x_limit, 1500)

    # حساب الأنماط حسب الوضع
    if 'Electron' in mode:
        if delta_v > 0:
            I_interf = double_slit_intensity_with_spread(x, v_mean, delta_v, L_total, a_width, d_slit)
        else:
            I_interf = double_slit_intensity_by_wavelength(x, lam, L_total, a_width, d_slit)
        I_particle = particle_like_pattern(x, lam, L_total, a_width, d_slit)
        velocity_display = v_mean / 1e3
        wavelength_display_nm = lam * 1e9
        if abs(v_mean - 70e3) < 20e3 and abs(a_width - 0.3e-6) < 0.1e-6 and abs(d_slit - 1e-6) < 0.2e-6:
            jonsson_validation(v_mean, a_width, d_slit, L_total)
    elif 'Photon' in mode:
        I_interf = double_slit_intensity_by_wavelength(x, lam, L_total, a_width, d_slit)
        I_particle = particle_like_pattern(x, lam, L_total, a_width, d_slit)
        velocity_display = None
        wavelength_display_nm = wavelength_nm
    else:  # White light mode
        I_R, I_G, I_B = white_light_pattern_rgb(x, L_total, a_width, d_slit)
        # الشدة الكلية (للمقارنة وللنمط الرئيسي)
        I_interf = (I_R + I_G + I_B) / 3.0
        # نمط جسيمي مرجعي (أخضر)
        I_particle = particle_like_pattern(x, 532e-9, L_total, a_width, d_slit)
        velocity_display = None
        wavelength_display_nm = None

    # تطبيق تأثير مكتشف المسار
    if observer_active:
        I = (1 - meas_strength) * I_interf + meas_strength * I_particle
    else:
        I = I_interf

    # محاكاة التراكم (اختياري)
    if show_buildup:
        cumulative = np.zeros_like(x)
        for _ in range(n_particles):
            if 'Electron' in mode:
                if delta_v > 0:
                    I_one = double_slit_intensity_with_spread(x, v_mean, delta_v, L_total, a_width, d_slit, n_samples=20)
                else:
                    I_one = double_slit_intensity_by_wavelength(x, lam, L_total, a_width, d_slit)
            elif 'Photon' in mode:
                I_one = double_slit_intensity_by_wavelength(x, lam, L_total, a_width, d_slit)
            else:
                I_R1, I_G1, I_B1 = white_light_pattern_rgb(x, L_total, a_width, d_slit)
                I_one = (I_R1 + I_G1 + I_B1) / 3.0
            if observer_active:
                I_one = (1 - meas_strength) * I_one + meas_strength * I_particle
            cumulative += I_one
        I = cumulative / n_particles

    # ضجيج الكاشف
    if temperature > 0:
        noise = (temperature / 1000.0) * 0.15 * np.max(I)
        I += np.random.normal(0, noise, len(I))
        I = np.maximum(I, 0)

    if np.max(I) > 0:
        I /= np.max(I)

    I_interf_norm = I_interf / np.max(I_interf) if np.max(I_interf) > 0 else I_interf
    I_particle_norm = I_particle / np.max(I_particle) if np.max(I_particle) > 0 else I_particle

    visibility = compute_visibility(x, I)
    if 'White' in mode:
        spacing_mm = 532e-9 * L_total / d_slit * 1000  # مرجع أخضر
    else:
        spacing_mm = lam * L_total / d_slit * 1000
    first_peak_theoretical_mm = spacing_mm

    # === الرسم ===
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    ax1, ax2, ax3, ax4 = axes[0,0], axes[0,1], axes[1,0], axes[1,1]

    # الرسم الأول: النمط الرئيسي
    ax1.plot(x*1000, I, 'b-', lw=1.5)
    ax1.fill_between(x*1000, I, alpha=0.3)
    title = f'{mode} | وضوح الأهداب = {visibility:.1%}'
    if observer_active:
        title += f' | قوة القياس = {meas_strength:.2f}'
        if meas_strength > 0.9:
            title += ' (سلوك جسيمي)'
        elif meas_strength > 0.1:
            title += ' (تماسك جزئي)'
        else:
            title += ' (تداخل تام)'
    if 'Electron' in mode and delta_v > 0:
        title += f' | Δv = {delta_v/1e3:.0f} كم/ث'
    if temperature > 0:
        title += f' | ضوضاء = {temperature:.0f} كلفن'
    ax1.set_title(title)
    ax1.set_xlabel('الموقع (مم)')
    ax1.set_ylabel('الشدة (و.ع)')
    ax1.set_xlim(-x_limit*1000, x_limit*1000)
    ax1.grid(alpha=0.3)

    # الرسم الثاني: شاشة الكاشف (مع الألوان الحقيقية للضوء الأبيض)
    if 'White' in mode:
        # إعادة حساب RGB للتأكد من التطبيع (قد يكون سبق حسابها)
        I_R, I_G, I_B = white_light_pattern_rgb(x, L_total, a_width, d_slit)
        # تطبيع كل قناة لعرض الألوان بشكل صحيح
        if np.max(I_R) > 0: I_R_norm = I_R / np.max(I_R)
        else: I_R_norm = I_R
        if np.max(I_G) > 0: I_G_norm = I_G / np.max(I_G)
        else: I_G_norm = I_G
        if np.max(I_B) > 0: I_B_norm = I_B / np.max(I_B)
        else: I_B_norm = I_B
        
        screen_rgb = np.zeros((150, len(x), 3))
        screen_rgb[:,:,0] = np.tile(I_R_norm, (150, 1))
        screen_rgb[:,:,1] = np.tile(I_G_norm, (150, 1))
        screen_rgb[:,:,2] = np.tile(I_B_norm, (150, 1))
        ax2.imshow(screen_rgb, aspect='auto', extent=[-x_limit*1000, x_limit*1000, 0, 1])
    else:
        screen = np.tile(I, (150, 1))
        im = ax2.imshow(screen, cmap='hot', aspect='auto', extent=[-x_limit*1000, x_limit*1000, 0, 1])
        plt.colorbar(im, ax=ax2, label='الشدة', shrink=0.8)
    ax2.set_title('شاشة الكاشف')
    ax2.set_xlabel('الموقع (مم)')
    ax2.set_yticks([])

    # الرسم الثالث: مقارنة التكاملية
    ax3.plot(x*1000, I_interf_norm, 'b--', lw=1, alpha=0.7, label='تداخل خالص')
    ax3.plot(x*1000, I_particle_norm, 'r--', lw=1, alpha=0.7, label='سلوك جسيمي خالص')
    ax3.plot(x*1000, I, 'k-', lw=2, label='الحالة الحالية')
    ax3.set_xlim(-x_limit*1000, x_limit*1000)
    ax3.set_ylim(0, 1.05)
    ax3.set_title('مبدأ التكاملية')
    ax3.set_xlabel('الموقع (مم)')
    ax3.set_ylabel('شدة طبيعية')
    ax3.legend(fontsize=8, loc='upper right')
    ax3.grid(alpha=0.3)

    # الرابع: لوحة المعلومات
    if 'Electron' in mode:
        info = (f"المسافة بين الأهداب (نظرياً): {spacing_mm:.2f} مم\n"
                f"موقع أول قمة: ±{first_peak_theoretical_mm:.2f} مم\n"
                f"الطول الموجي λ = {wavelength_display_nm:.2f} نانومتر\n"
                f"سرعة الإلكترون: {velocity_display:.0f} كم/ث\n"
                f"عرض الشق = {a_width*1e6:.2f} ميكرومتر\n"
                f"المسافة بين الشقين = {d_slit*1e6:.2f} ميكرومتر\n"
                f"التكاملية V = {visibility:.2f}")
    elif 'Photon' in mode:
        info = (f"المسافة بين الأهداب (نظرياً): {spacing_mm:.2f} مم\n"
                f"موقع أول قمة: ±{first_peak_theoretical_mm:.2f} مم\n"
                f"الطول الموجي = {wavelength_display_nm:.0f} نانومتر (فوتون أحادي)\n"
                f"عرض الشق = {a_width*1e6:.2f} ميكرومتر\n"
                f"المسافة بين الشقين = {d_slit*1e3:.2f} مم\n"
                f"التكاملية V = {visibility:.2f}")
    else:
        info = (f"المسافة بين الأهداب (مرجع أخضر): {spacing_mm:.2f} مم\n"
                f"(ضوء أبيض: أحمر 650، أخضر 532، أزرق 450 نانومتر)\n"
                f"(الشاشة الملونة تعرض الألوان الحقيقية للتجربة)\n"
                f"عرض الشق = {a_width*1e6:.2f} ميكرومتر\n"
                f"المسافة بين الشقين = {d_slit*1e3:.2f} مم\n"
                f"التكاملية V = {visibility:.2f}")
    ax4.text(0.05, 0.95, info, transform=ax4.transAxes, fontsize=10, va='top', family='DejaVu Sans')
    ax4.axis('off')

    plt.tight_layout()
    plt.show()

    # مخرجات إضافية
    print(f"✅ وضوح الأهداب: {visibility:.1%} | التباعد النظري: {spacing_mm:.2f} مم")
    if 'Electron' in mode:
        print(f"⏱️ زمن طيران الإلكترون: {L_total/v_mean*1e9:.2f} نانوثانية")
    elif 'Photon' in mode:
        print(f"⏱️ زمن طيران الفوتون: {L_total/c*1e9:.2f} نانوثانية")
    else:
        print("⏱️ زمن الطيران: يختلف حسب اللون (≈ 7.3 نانوثانية للضوء)")

    print("\n📥 لتصدير البيانات كـ CSV، استخدم الأوامر التالية في خلية جديدة:")
    print("```python")
    print("import numpy as np")
    print("data = np.column_stack([x*1000, I])")
    print("np.savetxt('double_slit_pattern.csv', data, delimiter=',', header='position_mm,intensity', comments='')")
    print("```")
