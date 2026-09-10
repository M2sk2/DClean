import os
import random
import openpyxl
from datetime import datetime, timedelta

def create_distraction_era_dataset(output_path: str):
    """
    Generates Dataset 1: Workshop 'Distraction_Era' (13 columns)
    Headers exactly matching guidelines image and DataGenerating.md.
    Includes controlled real-world anomalies:
    - Saudi phone numbers with dropped zeros (Excel bug), 00966, +96605...
    - Email typos (@gmaill.com, @hotmial.com) and extra whitespace
    - Arabic compound names ('عبد الله', 'سيف الدين', 'آل سعود')
    - Inverted English names ('Al-Harbi, Salman')
    - Excel serial floating timestamps (46266.6125) and string dates
    - Duplicate registrations with updated attendance/status
    - Missing identifier / spam quarantine rows
    """
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Distraction_Era_Raw"

    headers = [
        "FullName(AR)",
        "FullName(En)",
        "Email",
        "Phone",
        "Major",
        "Univeristy",
        "Academic lvl",
        "Where did you hear about about the workshop",
        "What to expect from the workshop",
        "Biggest source of distraction",
        "Agree to being photographed?",
        "Attendace",
        "TimeStamp"
    ]
    ws.append(headers)

    raw_records = [
        # Normal + Arabic compound 'عبد الله'
        ["عبد الله محمد السالم", "Abdullah Al-Salem", "abdullah.salem@gmail.com", "0507788990", "علوم حاسب", "جامعة الملك سعود", "سنة ثالثة", "تويتر / X", "فهم آليات التركيز وتقليل التشتت", "إشعارات الجوال ووسائل التواصل", "نعم", "حضر", "2026-09-01 10:15:00"],
        # Excel dropped zero bug ('508889900') + Excel serial float timestamp
        ["سارة بنت خالد بن سلطان", "Sarah Al-Sultan", "sarah.sultan@hotmail.com", 508889900, "نظم معلومات", "جامعة الأميرة نورة", "سنة ثانية", "صديق أو زميل", "أدوات عملية لزيادة الإنتاجية", "كثرة الاجتماعات والمقاطعات", "موافق", "حاضر", 46266.6125],
        # Double zero international prefix '00966...' + Email typo @gmaill.com
        ["محمد إبراهيم آل الشيخ", "Mohammed Al-Sheikh", "  mohammed.sheikh@gmaill.com  ", "00966531122334", "هندسة برمجيات", "KFUPM", "سنة رابعة", "لينكد إن", "تنظيم وقت المذاكرة والعمل", "التسويف وتأجيل المهام", "أوافق", "حضر", "2026-09-01 11:30:22"],
        # Patronymic compound 'آل سعود' + Redundant country code + local zero '+96605...'
        ["أحمد بن فهد آل سعود", "Ahmed Al-Saud", "ahmed.fahad@yahoo.com", "+9660554975066", "إدارة أعمال", "KSU", "خريج", "رسالة واتساب", "استراتيجيات الإنتاجية العالية", "تصفح المقاطع القصيرة", "نعم", "لم يحضر", "2026-09-01 12:00:00"],
        # Inverted English Name 'Al-Harbi, Salman' + University acronym 'UJ'
        ["سلمان نايف الحربي", "Al-Harbi, Salman", "salman.harbi@gmail.com", "0543217890", "ذكاء اصطناعي", "UJ", "سنة أولى", "إيميل الجامعة", "تطوير عادات التركيز العميق", "الضوضاء في بيئة العمل", "لا", "حضر", "2026-09-01 12:45:10"],
        # Honorific 'د.' + local Saudi 9665... without plus
        ["د. منيرة عبدالعزيز الشمري", "Dr. Muneera Al-Shammari", "muneera.shammari@gmail.com", "966551234987", "طب بشري", "جامعة الإمام عبدالرحمن بن فيصل", "سنة امتياز", "تويتر / X", "إدارة الضغوط والتشتت أثناء التدريب", "ضغط العمل وكثرة المهام", "موافق", "حضر", "2026-09-01 13:10:00"],
        # Compound 'سيف الدين' + Email typo @hotmial.com
        ["سيف الدين عمر البشير", "Saifeldin Al-Basheer", "saif.basheer@hotmial.com", "0569876543", "أمن سيبراني", "جامعة الإمام", "3", "مجموعة تيليجرام", "أفضل تقنيات البومودورو والتركيز", "ألعاب الفيديو", "نعم", "حاضر", 46266.6500],
        # Academic level numeric '2' + Formatting noise with dashes in phone
        ["ريما صالح القحطاني", "Reema Al-Qahtani", "reema.q@outlook.com", "+966-50-443-2211", "تصميم جرافيكي", "PNU", "2", "صديق", "التخلص من التشتت أثناء التصميم", "تطبيقات المحادثات الفورية", "أوافق", "غائب", "2026-09-01 14:00:00"],
        # English honorific 'Eng. Omar' + Float representation in phone from Excel
        ["عمر بن عبدالعزيز العتيبي", "Eng. Omar Al-Otaibi", "omar.otaibi@gmail.com", 966558536903.0, "هندسة صناعية", "جامعة الملك فهد للبترول والمعادن", "سنة رابعة", "لينكد إن", "أتمتة المهام لتقليل هدر الوقت", "المقاطعات المتكررة من الزملاء", "نعم", "حضر", "2026-09-01 14:30:15"],
        # Compound 'نور الهدى'
        ["نور الهدى عادل المالكي", "Noor Al-Huda Al-Malki", "noor.malki@gmail.com", "0591122334", "تقنية معلومات", "جامعة جدة", "سنة ثانية", "تويتر / X", "تحسين التركيز الذهني", "التفكير الزائد", "موافق", "حضر", "2026-09-01 15:00:00"],
        # Diacritics / Harakat in Arabic name
        ["مُحَمَّد عَبْدِ الرَّحْمَنِ الغَامِدِي", "Mohammed Al-Ghamdi", "m.ghamdi@hotmail.com", "0556677889", "علوم حاسب", "KAU", "سنة ثالثة", "نادي الكلية", "التغلب على التشتت الرقمي", "إشعارات اليوتيوب", "نعم", "حضر", "2026-09-01 15:20:00"],
        # Missing leading zero in 050 format ('501234567')
        ["شهد مساعد الزهراني", "Shahad Al-Zahrani", "shahad.z@gmail.com", "501234567", "إحصاء", "جامعة الملك سعود", "1", "تويتر", "التركيز على المذاكرة", "الجوال", "أوافق", "حاضر", "2026-09-01 15:40:00"],
        # Common English name + University variation
        ["Fahad Al-Dossary", "Fahad Al-Dossary", "fahad.dossary@gmail.com", "0549988776", "مالية", "King Saud University", "سنة رابعة", "لينكد إن", "زيادة الإنتاجية", "الأخبار ووسائل الإعلام", "نعم", "حضر", "2026-09-01 16:00:00"],
        # Female compound name
        ["فاطمة الزهراء علي الصالح", "Fatima Al-Saleh", "fatima.saleh@gmail.com", "0533344556", "صيدلة", "PNU", "سنة امتياز", "صديق", "إدارة الوقت", "التشتت الذهني", "نعم", "حضر", "2026-09-01 16:15:00"],
        # Phone with redundant international prefix + space
        ["خالد بن وليد المطيري", "Khaled Al-Mutairi", "khaled.m@hotmail.com", "+966 50 112 2334", "أمن سيبراني", "جامعة الإمام", "سنة ثالثة", "رسالة جامعية", "تقليل المشتتات", "التسويف", "موافق", "حاضر", "2026-09-01 16:30:00"],
        # Duplicate 1 (First submission of Tariq: absent)
        ["طارق زياد العلي", "Tariq Al-Ali", "tariq.ali@gmail.com", "0551122998", "ذكاء اصطناعي", "KSU", "سنة ثانية", "تويتر", "فهم التشتت", "الجوال", "نعم", "لم يحضر", "2026-09-01 09:00:00"],
        # Duplicate 1 (Second submission of Tariq: updated to attended + newer timestamp)
        ["طارق زياد العلي", "Tariq Al-Ali", "tariq.ali@gmail.com", "0551122998", "ذكاء اصطناعي", "KSU", "سنة ثانية", "تويتر", "فهم التشتت وأساليب التركيز", "الجوال والإشعارات", "نعم", "حضر", "2026-09-01 17:00:00"],
        # Duplicate 2 (First submission of Layan)
        ["ليان بدر الشريف", "Layan Al-Sharif", "layan.sharif@gmail.com", "0509988112", "نظم معلومات", "جامعة جدة", "سنة ثالثة", "لينكد إن", "التركيز في بيئة الدراسة", "وسائل التواصل", "موافق", "حضر", "2026-09-01 10:00:00"],
        # Duplicate 2 (Second submission of Layan: same person, slightly varied phone format)
        ["ليان بدر الشريف", "Layan Al-Sharif", "layan.sharif@gmail.com", "+966509988112", "نظم معلومات", "جامعة جدة", "سنة ثالثة", "لينكد إن", "التركيز في بيئة الدراسة والعمل", "وسائل التواصل والمحادثات", "موافق", "حضر", "2026-09-01 17:30:00"],
        # Participant who will ALSO appear in Dataset 2 (Cross-dataset entity resolution test!)
        ["عبدالعزيز سعود العريفي", "Abdulaziz Al-Arefe", "a.arefe@gmail.com", "0554433221", "علوم حاسب", "جامعة الملك سعود", "سنة رابعة", "تويتر", "أدوات تقليل التشتت", "الرسائل الفورية", "نعم", "حضر", "2026-09-01 18:00:00"],
        # Participant 2 who will ALSO appear in Dataset 2
        ["هند ناصر السبيعي", "Hind Al-Subaie", "hind.subaie@gmail.com", "0502233445", "هندسة برمجيات", "PNU", "سنة ثالثة", "نادي الكلية", "تنظيم ساعات البرمجة", "المقاطعات المتكررة", "موافق", "حضر", "2026-09-01 18:15:00"],
        # Academic level unusual string (preserve as is, no pseudo-normalization!)
        ["ياسر حمدان العنزي", "Yasser Al-Enezi", "yasser.enezi@gmail.com", "0567788990", "فيزياء", "KSU", "طالب زائر", "تويتر", "طرق التركيز", "الجوال", "نعم", "حاضر", "2026-09-01 18:30:00"],
        # Another standard valid row
        ["أروى طلال الحربي", "Arwa Al-Harbi", "arwa.harbi@gmail.com", "0534455667", "ذكاء اصطناعي", "جامعة الملك عبدالعزيز", "بكالوريوس - سنة 2", "صديق", "الاستفادة من الورشة", "الإشعارات", "نعم", "حضر", "2026-09-01 18:45:00"],
        ["بدر محمد القاسم", "Bader Al-Qasim", "bader.qasim@outlook.com", "0559988443", "مالية", "جامعة الإمام", "سنة ثانية", "لينكد إن", "زيادة التركيز", "المشتتات الخارجية", "لا", "حضر", "2026-09-01 19:00:00"],
        ["دلال إبراهيم المنصور", "Dalal Al-Mansour", "dalal.mansour@gmail.com", "0541122887", "إدارة أعمال", "جامعة الأميرة نورة", "سنة رابعة", "تويتر", "مهارات الإنجاز", "كثرة المهام", "موافق", "حضر", "2026-09-01 19:15:00"],
        ["فيصل سعد الدوسري", "Faisal Al-Dossary", "faisal.s.d@gmail.com", "0506677112", "هندسة حاسب", "KFUPM", "سنة ثالثة", "إيميل الجامعة", "التركيز في مشاريع التخرج", "الألعاب", "نعم", "حاضر", "2026-09-01 19:30:00"],
        ["جمانة عادل بخش", "Jomana Bakhsh", "jomana.b@gmail.com", "0598877665", "تصميم تفاعلي", "جامعة جدة", "سنة ثانية", "تويتر", "تطوير بيئة عمل هادئة", "الضجيج", "أوافق", "حضر", "2026-09-01 19:45:00"],
        ["كريم عبدالله النجار", "Kareem Al-Najjar", "kareem.n@gmail.com", "0543322119", "نظم معلومات", "جامعة الملك سعود", "سنة رابعة", "واتساب", "تقليل التسويف", "التواصل الاجتماعي", "نعم", "حضر", "2026-09-01 20:00:00"],
        ["مها ناصر الشهري", "Maha Al-Shehri", "maha.shehri@gmail.com", "0557766554", "علوم حاسب", "KAU", "سنة ثالثة", "لينكد إن", "التركيز الذهني", "المقاطعات", "موافق", "حاضر", "2026-09-01 20:15:00"],
        ["نايف سلطان العتيبي", "Naif Al-Otaibi", "naif.s.otaibi@gmail.com", "0508899776", "هندسة ميكانيكية", "KFUPM", "سنة رابعة", "تويتر", "تنظيم الوقت بين الدراسة والمشاريع", "الجوال", "نعم", "حضر", "2026-09-01 20:30:00"],
        ["رغد خالد التميمي", "Raghad Al-Tamimi", "raghad.tamimi@hotmail.com", "0531144778", "أمن معلومات", "جامعة الإمام", "سنة ثانية", "زميل", "إدارة الوقت والتركيز", "إشعارات التطبيقات", "أوافق", "حاضر", "2026-09-01 20:45:00"],
        ["سلطان ماجد الشريف", "Sultan Al-Sharif", "sultan.sharif@gmail.com", "0549922331", "ذكاء اصطناعي", "جامعة جدة", "سنة أولى", "تويتر", "التركيز الدراسي", "التشتت", "نعم", "حضر", "2026-09-01 21:00:00"],
        ["وفاء منصور السعيد", "Wafa Al-Saeed", "wafa.saeed@gmail.com", "0553311992", "إحصاء وتحليل بيانات", "PNU", "سنة رابعة", "لينكد إن", "تحسين جودة الإنتاج", "كثرة الأفكار غير المنظمة", "موافق", "حاضر", "2026-09-01 21:15:00"],
        ["يوسف إبراهيم الخالدي", "Youssef Al-Khaldi", "youssef.k@gmail.com", "0501199884", "هندسة برمجيات", "KSU", "سنة ثالثة", "إيميل الجامعة", "تجنب التسويف في البرمجة", "المقاطع القصيرة", "نعم", "حضر", "2026-09-01 21:30:00"],
        ["زينب علي المهنا", "Zainab Al-Muhanna", "zainab.m@gmail.com", "0564433882", "تصميم جرافيك", "جامعة الإمام عبدالرحمن بن فيصل", "سنة ثانية", "تويتر", "إتقان التركيز العميق", "الرسائل والإيميلات", "أوافق", "حاضر", "2026-09-01 21:45:00"],
        ["وليد صالح الغامدي", "Waleed Al-Ghamdi", "waleed.gh@gmail.com", "0503344778", "إدارة أعمال", "KAU", "خريج", "لينكد إن", "الإنتاجية في بيئة العمل", "الاجتماعات غير المجدية", "نعم", "حضر", "2026-09-01 22:00:00"],
        ["نجلاء سعد القحطاني", "Najla Al-Qahtani", "najla.q@gmail.com", "0558822334", "تسويق رقمي", "PNU", "سنة ثالثة", "صديق", "إدارة المهام بكفاءة", "الإشعارات", "موافق", "حاضر", "2026-09-01 22:15:00"],

        # QUARANTINE ROW 1: Missing Name entirely (Fails identity contract assertion)
        ["", "", "anonymous.user@gmail.com", "0501122334", "علوم حاسب", "KSU", "سنة أولى", "تويتر", "تجربة", "لا يوجد", "نعم", "حضر", "2026-09-01 22:30:00"],
        # QUARANTINE ROW 2: Missing Phone AND missing Email (Record cannot be linked or identified)
        ["علي حسن العبدلي", "Ali Al-Abdali", None, None, "هندسة", "KAU", "سنة ثانية", "تويتر", "لا شيء", "الجوال", "نعم", "حضر", "2026-09-01 22:45:00"],
        # QUARANTINE ROW 3: Spam test row with 'test test' and dummy phone '12345'
        ["test test", "test test", "test@test.com", "12345", "test", "test", "test", "test", "test", "test", "لا", "غائب", "2026-09-01 23:00:00"]
    ]

    for row in raw_records:
        ws.append(row)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    wb.save(output_path)
    print(f"[Success] Generated Dataset 1: {output_path} ({len(raw_records)} rows)")

def create_developers_committee_dataset(output_path: str):
    """
    Generates Dataset 2: 'نموذج طلب الانضمام إلى لجنة المطورين لعام 2026 (Responses)'
    Contains all 55 exact questions specified by the user!
    Includes:
    - Saudi phones with anomalies (+966, dropped zeros, 00966)
    - Gmail and University emails
    - Overlapping participants from Dataset 1 (Abdulaziz Al-Arefe, Hind Al-Subaie)
    - Multi-select skills and tech tools
    - Realistic free-form developer responses
    - Quarantine test row
    """
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Form Responses 1"

    headers = [
        "Timestamp",
        "الاسم الثلاثي بالعربي",
        "الاسم الثلاثي بالانجليزي",
        "الجنس",
        "رقم الجوال",
        "البريد الإلكتروني (Gmail)",
        "البريد الإلكتروني (الجامعي)",
        "الفرع",
        "التخصص الجامعي",
        "هل أنت/ي عضو في مجتمع قوقل؟",
        "اذا نعم، ماهي لجنتك؟",
        "شاركنا حسابك في (LinkedIn)",
        "اختر اللجنة الفرعية التي ترغب بالعمل عليها داخل لجنة المطورين",
        "اختر الدور الذي تراه مناسبًا لك داخل اللجنة",
        "كيف تقيّم مستواك الحالي في هذا المجال؟",
        "كم ساعة تستطيع الالتزام بها أسبوعيًا؟",
        "ما الذي يدفعك للعمل على هذا المشروع تحديدا؟",
        "ما هي مهاراتك التقنية ذات الصلة؟",
        "صف بإيجاز أي مشروع او خبرة سابقة لك في هذا المجال",
        "لماذا ترغب في العمل على هذا المشروع، وما القيمة التي يمكنك إضافتها للفريق؟",
        "ما التحدي الأكبر الذي قد تواجهه؟",
        "اختر الدور الذي تراه مناسبًا لك داخل اللجنة 2",
        "كيف تقيّم مستواك الحالي في هذا المجال؟ 2",
        "كم ساعة تستطيع الالتزام بها أسبوعيًا؟ 2",
        "هل درست أي مقرر له علاقة بتحليل البيانات؟\n(قواعد بيانات، Python، Data Science، إحصاء)",
        "ما الأدوات أو اللغات التي لديك معرفة بها؟",
        "برأيك، ما دور تحليل البيانات في أي مشروع؟",
        "هل سبق لك العمل على مشروع تحليلي (جامعي أو شخصي)؟",
        "إذا نعم، صفه باختصار",
        "لو كان لدينا بيانات حضور فعاليات، ما أول شيء تحب تحليله ولماذا؟",
        "لماذا ترغب في العمل على هذا المشروع، وما القيمة التي يمكنك إضافتها للفريق؟ 2",
        "ما التحدي الأكبر الذي قد تواجهه؟2",
        "اختر الدور الذي تراه مناسبًا لك داخل اللجنة3",
        "كيف تقيّم مستواك الحالي في هذا المجال؟ 3",
        "3 كم ساعة تستطيع الالتزام بها أسبوعيًا؟",
        "هل شاركت في مشروع تقني جماعي؟ اوصف دورك",
        "هل سبق لك العمل على تصميم الواجهات؟",
        "اذا نعم، ايش الادوات اللي استخدمتها؟",
        "؟ CSS / HTML / JavaScript هل لديك معرفة بـ",
        "هل استخدمت React؟",
        "هل اشتغلت على ربط API سابقا؟",
        "هل استخدمت OpenAI?",
        "لماذا ترغب في العمل على هذا المشروع، وما القيمة التي يمكنك إضافتها للفريق؟ 3",
        "ما التحدي الأكبر الذي قد تواجهه؟",
        "اختر الدور الذي تراه مناسبًا لك داخل اللجنة 4",
        "كيف تقيّم مستواك الحالي في هذا المجال؟ 4",
        "كم ساعة تستطيع الالتزام بها أسبوعيًا؟",
        "4هل سبق لك إنشاء سير عمل مؤتمت؟\tماهي المنصات التي استخدمتها؟",
        "صف بإيجاز ما قمت بإنشائه",
        "هل سبق لك العمل مع Ai agents or LLM tools ؟",
        "ماهي المحفزات/الإجراءات التي استخدمتها؟",
        "إذا كانت الأجابة نعم، إذا ما الذي قمت به باستخدامها؟",
        "قيم مدى ارتياحك لتصميم prompts لضمان اتساق التقييم (من 1 إلى 5)",
        "لماذا ترغب في العمل على هذا المشروع، وما القيمة التي يمكنك إضافتها للفريق؟ 4",
        "ما التحدي الأكبر الذي قد تواجهه؟3"
    ]
    ws.append(headers)

    # Cross-dataset entity 1: Abdulaziz Al-Arefe (Registered in Workshop, now applying to Developers Committee!)
    # Same canonical phone (+966554433221) and email, proving cross-dataset entity resolution!
    p1 = [
        "2026-09-02 09:14:22",
        "عبدالعزيز سعود العريفي", "Abdulaziz Al-Arefe", "ذكر",
        "0554433221", "a.arefe@gmail.com", "441102938@student.ksu.edu.sa",
        "الرياض - الدرعية", "علوم حاسب", "نعم", "لجنة الذكاء الاصطناعي", "https://linkedin.com/in/arefe-dev",
        "لجنة الذكاء الاصطناعي وتحليل البيانات", "مهندس بيانات / Data Engineer", "متقدم (4)", "10 - 15 ساعة",
        "الشغف ببناء أنظمة معالجة وتنظيف البيانات وتطوير مشاريع المجتمع",
        "Python, SQL, DuckDB, Pandas, FastAPI", "بناء خط معالجة بيانات للأنشطة الطلابية باستخدام بايثون",
        "خبرة في هندسة البيانات وبناء pipelines قوية وموثوقة", "التنسيق بين الفرق وضيق الوقت الدراسي",
        "مطور واجهات خلفية (Backend)", "متوسط (3)", "5 - 10 ساعات",
        "نعم (درست قواعد بيانات وعلوم بيانات وتحليل إحصائي)",
        "Python, PostgreSQL, Git, Docker", "اتخاذ قرارات مبنية على حقائق وتحسين تجربة المستفيدين",
        "نعم", "تحليل معدلات بقاء الطلاب والتسجيل في المقررات",
        "معدل الحضور الفعلي مقارنة بالتسجيل لمعرفة أسباب الغياب", "تقديم تحليلات دقيقة تساعد اللجنة في التخطيط",
        "تنظيف البيانات غير المنظمة", "عضو فريق تقني", "متوسط (3)", "5 ساعات",
        "نعم، كنت مسؤولاً عن تطوير الـ Backend وربط قاعدة البيانات", "نعم", "Figma",
        "نعم، معرفة جيدة", "نعم", "نعم", "نعم",
        "تقديم حلول تكاملية شاملة", "إدارة الوقت", "مطور حلول ذكاء اصطناعي", "متقدم (4)", "10 ساعات",
        "نعم، استخدمت Make وZapier وGitHub Actions", "أتمتة إرسال رسائل القبول وإشعارات التيليجرام",
        "نعم", "LangChain, AutoGen, OpenAI Assistants API",
        "بناء مساعد ذكي يجيب على استفسارات الطلاب من واقع اللائحة", "4",
        "تسخير الذكاء الاصطناعي التوليدي لخدمة الطلاب", "دقة المخرجات والحد من الهلوسة"
    ]

    # Cross-dataset entity 2: Hind Al-Subaie (Also present in Workshop)
    p2 = [
        "2026-09-02 10:20:15",
        "هند ناصر السبيعي", "Hind Al-Subaie", "أنثى",
        "+966502233445", "hind.subaie@gmail.com", "h.subaie@pnu.edu.sa",
        "الرياض - مطار الملك خالد", "هندسة برمجيات", "نعم", "لجنة التطوير", "https://linkedin.com/in/hind-subaie",
        "لجنة الويب وتطبيقات الجوال", "مطورة Full Stack", "متقدم (4)", "8 - 12 ساعة",
        "تطوير منصات برمجية تخدم طلاب وطالبات الجامعات",
        "React, TypeScript, Next.js, Tailwind CSS, Node.js", "تطوير لوحة تحكم لإدارة فعاليات النادي بالرياكت",
        "تصميم وبرمجة واجهات استخدام عصرية وسريعة الاستجابة", "الموازنة بين ساعات الدراسة ومواعيد التسليم",
        "مصممة تجربة مستخدم (UI/UX)", "متقدم (4)", "6 - 8 ساعات",
        "نعم (درست قواعد بيانات وبايثون)", "SQL, Python, JavaScript, Figma",
        "فهم سلوك المستخدم وتحسين واجهات التطبيق وفق البيانات",
        "نعم", "تحليل استبيانات رضا المستخدمين عن المنصة التعليمية",
        "أوقات الذروة في التسجيل وتفاعل المستخدمين", "تطوير تجارب تفاعلية تزيد الإقبال",
        "التعامل مع بيانات غير مكتملة", "قائدة فريق الواجهات", "متقدم (4)", "8 ساعات",
        "نعم، قائدة فريق في هاكاثون الذكاء الاصطناعي بالرياض", "نعم", "Figma, Adobe XD",
        "نعم، معرفة متقدمة", "نعم، أستخدمه بشكل رئيسي", "نعم، خبرة واسعة", "نعم",
        "رفع جودة الواجهات وتطبيق معايير الوصول العالمية", "التوافق مع متصفحات مختلفة",
        "مطورة وكلاء ذكاء اصطناعي", "متوسط (3)", "6 ساعات",
        "نعم، n8n وGitHub Actions", "أتمتة بناء واختبار التطبيقات ونشرها على Vercel",
        "نعم", "OpenAI API, Cursor, Claude Code",
        "دمج أدوات التلخيص التلقائي للمستندات في الموقع", "5",
        "تكامل التقنيات الحديثة في الواجهات", "إدارة التكاليف وسرعة الاستجابة"
    ]

    # Additional diverse participants (3 to 30)
    names_and_data = [
        ("سلطان بن عبدالعزيز آل سعود", "Sultan Al-Saud", "ذكر", "0501144778", "sultan.saud@gmail.com", "الرياض", "نظم معلومات"),
        ("ريم بنت تركي بن مقرن", "Reem Al-Muqrin", "أنثى", "507788112", "reem.muqrin@hotmail.com", "جدة", "علوم حاسب"),
        ("عبدالله بن باز الغامدي", "Abdullah Bin Baz", "ذكر", "00966533221144", "a.binbaz@gmaill.com", "الظهران", "هندسة برمجيات"),
        ("فيصل أحمد الشهري", "Faisal Al-Shehri", "ذكر", "+9660551188442", "faisal.sh@gmail.com", "أبها", "أمن سيبراني"),
        ("شروق عبدالله الحربي", "Shorooq Al-Harbi", "أنثى", "0543219900", "shorooq.h@gmail.com", "المدينة المنورة", "ذكاء اصطناعي"),
        ("عمر خالد الدوسري", "Omar Al-Dossary", "ذكر", "0561122334", "omar.d@gmail.com", "الدمام", "علوم حاسب"),
        ("أثير ماجد القحطاني", "Atheer Al-Qahtani", "أنثى", "0509988771", "atheer.q@outlook.com", "الرياض", "إحصاء"),
        ("سعود فهد العتيبي", "Saud Al-Otaibi", "ذكر", "0554411223", "saud.otaibi@gmail.com", "الطائف", "هندسة صناعية"),
        ("نجود صالح المالكي", "Nojood Al-Malki", "أنثى", "0598811223", "nojood.m@gmail.com", "مكة المكرمة", "تقنية معلومات"),
        ("ياسين عبدالرحمن الشمري", "Yaseen Al-Shammari", "ذكر", "0544433221", "yaseen.sh@gmail.com", "حائل", "هندسة حاسب"),
        ("غادة فهد المطيري", "Ghada Al-Mutairi", "أنثى", "0502211334", "ghada.m@gmail.com", "القصيم", "نظم معلومات"),
        ("تركي محمد السالم", "Turki Al-Salem", "ذكر", "0556655443", "turki.salem@gmail.com", "الرياض", "ذكاء اصطناعي"),
        ("لجين عصام البشير", "Lojain Al-Basheer", "أنثى", "0533322119", "lojain.b@gmail.com", "جدة", "تصميم جرافيك"),
        ("مشاري نواف العنزي", "Mishari Al-Enezi", "ذكر", "0566677889", "mishari.e@gmail.com", "تبوك", "علوم حاسب"),
        ("سارة وليد الصالح", "Sarah Al-Saleh", "أنثى", "0541199882", "sarah.saleh@gmail.com", "الأحساء", "هندسة برمجيات"),
        ("راكان فهد الخالدي", "Rakan Al-Khaldi", "ذكر", "0503322114", "rakan.k@gmail.com", "الخبر", "أمن سيبراني"),
        ("طيف ناصر الزهراني", "Taif Al-Zahrani", "أنثى", "0551133557", "taif.z@gmail.com", "الباحة", "تقنية معلومات"),
        ("ماجد يوسف الغامدي", "Majed Al-Ghamdi", "ذكر", "0548877665", "majed.gh@gmail.com", "جدة", "إدارة أعمال"),
        ("روان طارق العلي", "Rawan Al-Ali", "أنثى", "0507766554", "rawan.ali@gmail.com", "الرياض", "علوم حاسب"),
        ("خالد فهد الجبير", "Khaled Al-Jubeir", "ذكر", "0554499881", "khaled.j@gmail.com", "الرياض", "علوم حاسب")
    ]

    all_rows = [p1, p2]

    for idx, (ar_n, en_n, g, ph, em, city, maj) in enumerate(names_and_data, start=3):
        # Generate varied realistic answers across all 55 questions
        row = [
            f"2026-09-02 {10 + (idx % 12):02d}:{idx * 2 % 60:02d}:00",
            ar_n, en_n, g, ph, em, f"{em.split('@')[0]}@student.edu.sa",
            f"فرع {city}", maj,
            "نعم" if idx % 2 == 0 else "لا",
            "لجنة المطورين" if idx % 2 == 0 else "",
            f"https://linkedin.com/in/{en_n.lower().replace(' ', '-')}",
            "لجنة الذكاء الاصطناعي وتحليل البيانات" if idx % 3 == 0 else ("لجنة الويب والواجهات" if idx % 3 == 1 else "لجنة الأتمتة والسحابة"),
            "عضو مطور" if idx % 2 == 0 else "قائد فريق فرعي",
            f"مستوى {idx % 5 + 1}",
            f"{5 + (idx % 10)} ساعات",
            "الشغف بالبرمجة والمساهمة في بناء مشاريع تقنية مميزة تخدم الطلاب",
            "Python, React, SQL, Git" if idx % 2 == 0 else "Java, Flutter, Firebase",
            "مشاريع جامعية وهاكاثونات سابقة",
            "التفاني في العمل الجماعي وتسليم المهام بدقة وجودة عالية",
            "تنظيم الوقت وضغط الدراسة",
            "مطور" if idx % 2 == 0 else "باحث بيانات",
            f"{idx % 4 + 1}",
            f"{4 + idx % 8} ساعات",
            "نعم" if idx % 2 == 0 else "لا، لكن لدي رغبة بالتعلم",
            "Python, SQL, Excel" if idx % 2 == 0 else "R, SPSS",
            "تحويل الأرقام الخام إلى رؤى تفيد إدارة المشروع في التطوير",
            "نعم" if idx % 2 == 0 else "لا",
            "تحليل بيانات طلاب الكلية" if idx % 2 == 0 else "",
            "نسب الحضور ونسب إكمال المهام لمعرفة مدى الالتزام",
            "بناء تقارير تفاعلية عبر PowerBI أو Dashboards",
            "البيانات غير النظيفة أو المكررة",
            "عضو دعم فني",
            f"{idx % 4 + 1}",
            f"{5 + idx % 5} ساعات",
            "نعم، شاركت في مشروع تخرج جماعي وكنت مسؤول التوثيق والبرمجة",
            "نعم" if idx % 2 == 0 else "لا",
            "Figma" if idx % 2 == 0 else "",
            "نعم" if idx % 2 == 0 else "أساسيات فقط",
            "نعم" if idx % 3 == 0 else "لا",
            "نعم" if idx % 2 == 0 else "لا",
            "نعم" if idx % 2 == 0 else "لا",
            "تطوير أدوات تسهل حياة الطلاب",
            "الوقت والمهام المفاجئة",
            "مطور ذكاء اصطناعي",
            f"{idx % 5 + 1}",
            f"{6 + idx % 6} ساعات",
            "نعم، استخدمت Zapier" if idx % 2 == 0 else "لا",
            "أتمتة تنبيهات الفعاليات وتحديث جداول Google Sheets",
            "نعم" if idx % 2 == 0 else "لا",
            "LangChain, HuggingFace" if idx % 2 == 0 else "ChatGPT Web",
            "بناء بوت تلخيص المقالات الأكاديمية",
            str(random.randint(3, 5)),
            "ابتكار أفكار جديدة وإيجاد حلول ذكية للتحديات",
            "صعوبة ضبط أداء النماذج أحياناً"
        ]
        all_rows.append(row)

    # Add a Quarantine Row in Dataset 2: Missing Name and Missing phone
    quarantine_row = [
        "2026-09-02 23:59:00",
        "", "", "ذكر", "", "invalid.no.name@gmail.com", "",
        "الرياض", "حاسب", "لا", "", "", "لجنة الذكاء الاصطناعي",
        "عضو", "1", "2 ساعة", "لا شيء", "لا يوجد", "لا يوجد",
        "لا يوجد", "لا يوجد", "", "", "", "لا", "لا يوجد", "لا يوجد",
        "لا", "", "", "", "", "", "", "", "لا", "لا", "", "لا", "لا",
        "لا", "لا", "", "", "", "", "", "لا", "", "لا", "", "", "1", "", ""
    ]
    all_rows.append(quarantine_row)

    for r in all_rows:
        ws.append(r)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    wb.save(output_path)
    print(f"[Success] Generated Dataset 2: {output_path} ({len(all_rows)} rows, 55 columns)")

def create_multisheet_dataset(output_path: str):
    """
    Generates Dataset 3: Multi-Sheet Excel Workbook
    Has 2 sheets: 'Morning_Session' and 'Evening_Session'
    Contains shared participants across both sheets to verify multi-sheet processing
    and cross-sheet entity deduplication.
    """
    wb = openpyxl.Workbook()
    
    # Sheet 1: Morning Session
    ws1 = wb.active
    ws1.title = "Morning_Session"
    headers = ["FullName(AR)", "FullName(En)", "Email", "Phone", "Major", "Univeristy", "Academic lvl", "TimeStamp"]
    ws1.append(headers)
    ws1.append(["عبدالله محمد السالم", "Abdullah Al-Salem", "abdullah.salem@gmail.com", "0507788990", "علوم حاسب", "جامعة الملك سعود", "سنة ثالثة", "2026-09-03 09:00:00"])
    ws1.append(["سارة خالد السلطان", "Sarah Al-Sultan", "sarah.sultan@hotmail.com", "0508889900", "نظم معلومات", "جامعة الأميرة نورة", "سنة ثانية", "2026-09-03 09:15:00"])
    ws1.append(["فهد ناصر الدوسري", "Fahad Al-Dossary", "fahad.d@gmail.com", "0549988776", "مالية", "KSU", "سنة رابعة", "2026-09-03 09:30:00"])

    # Sheet 2: Evening Session
    ws2 = wb.create_sheet(title="Evening_Session")
    ws2.append(headers)
    # Abdullah Al-Salem attends evening session too! (Duplicate person across sheets)
    ws2.append(["عبدالله محمد السالم", "Abdullah Al-Salem", "abdullah.salem@gmail.com", "+966507788990", "علوم حاسب", "جامعة الملك سعود", "سنة ثالثة", "2026-09-03 16:00:00"])
    ws2.append(["نورة سعد القحطاني", "Noura Al-Qahtani", "noura.q@gmail.com", "0551122334", "ذكاء اصطناعي", "PNU", "سنة أولى", "2026-09-03 16:30:00"])

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    wb.save(output_path)
    print(f"[Success] Generated Dataset 3 (Multi-Sheet): {output_path} (2 sheets)")

def main():
    base_dir = os.path.abspath("RawData")
    create_distraction_era_dataset(os.path.join(base_dir, "Distraction_Era_Workshop_Dataset.xlsx"))
    create_developers_committee_dataset(os.path.join(base_dir, "Developers_Committee_2026_Responses.xlsx"))
    create_multisheet_dataset(os.path.join(base_dir, "MultiSheet_Workshop_Batches.xlsx"))

if __name__ == "__main__":
    main()
