from google.adk.agents import Agent

from .tools import get_current_time

# Add in-memory knowledge base entries
knowledge = [
    {
        "title": "ข้อมูลทั่วไปบริษัท",
        "content": (
            "ชื่อบริษัท: บริษัท วันทูออล จํากัด\n"
            "ที่อยู่: เลขที่ 359 ถึง 363 ถนน ประชาอุทิศ แขวง เขตห้วยขวาง กรุงเทพ\n"
            "โทร: 02 690-3626\n"
            "ก่อตั้ง: ปี 2005 (20 ปี)   |   รายได้ล่าสุด: 680 ลบ.\n"
            "ลูกค้าองค์กร มากกว่า 4,500 ราย  ใบอนุญาต NBTC Type 3 (ปี 2025)"
        )
    },
    {
        "title": "ไทม์ไลน์ความเติบโต",
        "content": (
            "2005  ก่อตั้ง (VoIP)\n"
            "2010  ลูกค้าเสียง 250 ราย\n"
            "2015 รุก Data Connectivity\n"
            "2019 Zoom Partner แรกในไทย (รายได้ 208 ลบ.)\n"
            "2024 Tencent Cloud & AI Distributor (รายได้ 680 ลบ.)\n"
            "2025 ได้ใบอนุญาต NBTC Type 3 (Tier 1 Telecom)"
        )
    },
    {
        "title": "ความเชี่ยวชาญหลัก",
        "content": (
            "Cyber Security, Cloud Computing, Artificial Intelligence,\n"
            "Voice & Data Networking, Meeting Solutions, Audio-Visual,\n"
            "System Integration, Acoustic Solutions"
        )
    },
    {
        "title": "สินค้าและบริการหลัก",
        "content": (
            "Cyber Security AI Autopilot, Infra/App/OT Security, Red/Blue Team\n"
            "Telecom Domestic & Intl Voice, DID, SMS, AI Voice Bot\n"
            "Data & Network Internet (SLA 99.999%), SD-WAN, SASE\n"
            "Comm/Collab Zoom (Premium Partner), MS Teams, UCaaS\n"
            "Cloud Multi-/Hybrid Cloud, Tencent Cloud Distributor\n"
            "A/V & Meeting LED Wall, Immersive XR, Smart Room, AI Transcription\n"
            "AI Solutions GenAI Agent (PQ-encrypted), STT TH 99.99%\n"
            "Training Academy AI, Cyber, EV (4-month bootcamp)"
        )
    },
    {
        "title": "พันธมิตร/รางวัลเด่น",
        "content": (
            "Zoom (Platinum Partner รายเดียวในไทย), Tencent Cloud\n"
            "Microsoft Teams, Securonix, Positive Technologies"
        )
    },
    {
        "title": "จุดเด่นด้าน Cyber Security",
        "content": (
            "ตรวจสอบช่องโหว่\n"
            "Ethical Hackers 100+\n"
        )
    },
    {
        "title": "บริการหลังการขาย",
        "content": (
            "Call Center 1605\n"
            "ทีมผู้เชี่ยวชาญใช้และจำหน่ายโซลูชันเดียวกันกับลูกค้า"
        )
    },
    {
        "title": "วิสัยทัศน์ขององค์กร",
        "content": (
            "เป็นผู้เล่นหลัก ด้านการเปลี่ยนนแปลงทางดิจิทัลในระดับใหญ"
        )
    },
    {
        "title": "พันธกิจขององค์กร",
        "content": (
            "เพิ่มศักยภาพให้ลูกค้าด้วยสินค้าและโซลูช่ันที่มีคุณค่า ล้ำหน้า ใช้ง่ายและใช้ได้จริง"
        )
    },
    {
    "title": "CORE VALUE",
    "content": (
        "INITIATIVE : ริเริ่ม\n"
        "MOVE FAST : ทำเร็ว\n"
        "SINCERE : จริงใจ\n"
        "COMMIT : คำมั่น\n"
        "CREATIVE : สร้างสรรค์\n"
        "OUTCOME : เน้นผล\n"
        "RESPECT : ให้เกียรติ\n"
        "TEAMWORK : ทีมเวิร์ค\n"
    )
    },
    {
        "title": "OUR CULTURE",
        "content": (
            "01 เรา BAN คํานี้ \"งานใครงานมัน อย่าไปยุ่ง\"\n"
            "02 ลูกค้าอันดับหนึ่ง\n"
            "03 ทดลองและล้มเหลวได้\n"
        )
    },
    {
        "title": "ระเบียบการแต่งกายพนักงาน",
        "content":(
            "วัตถุประสงค์: สร้างภาพลักษณ์ที่เป็นมืออาชีพและสภาพแวดล้อมการทำงานที่เหมาะสม\n"
            "พนักงานชาย\n"
            "เสื้อเชิ้ตยูนิฟอร์มบริษัท เสื้อโปโล หรือเชิ้ตคอจีน สีสุภาพ\n"
            "แจ็กเก็ตสีสุภาพ ไม่มีลวดลาย ห้ามใส่หนังและยีนส์ \n"
            "กางเกงขายาว ผ้าสีสุภาพหรือยีนส์ไม่ขาด\n"
            "รองเท้า คัทชู หุ้มส้น หรือผ้าใบทรงสุภาพ\n"
            "ห้ามใส่เสื้อกล้าม แขนกุด ยืดคอกลม ยกเว้นมีสูทคลุม\n"
            "พนักงานหญิง\n"
            "เสื้อไม่เว้า เดรส เชิ้ต ยูนิฟอร์มบริษัท เสื้อโปโลคอปก-คอจีน\n"
            "กระโปรงเหนือเข่า 3 นิ้ว หรือกางเกงขายาว ส่วน ผ้าสีสุภาพหรือยีนส์ไม่ขาด\n"
            "แจ็กเก็ตสีสุภาพ ไม่มีลวดลาย\n"
            "รองเท้า คัทชู หุ้มส้น ส้นสูง สายรัดส้น หรือผ้าใบทรงสุภาพ\n"
            "ห้าม : เสื้อซีทรู, สายเดี่ยว เกาะอก เปิดไหล่, ยีนส์ขาด, เสื้อยืดคอกลม"
        )
    },
    {
        "title": "ระเบียบการลา",
        "content":(
            "ยกเลิกการแจ้งลาหยุดงานผ่านกลุ่ม 1toall ใน Dingtalk\n"
            "การลาหยุดงานต้องแจ้งให้ผู้บังคับบัญชาทราบล่วงหน้าตามข้อบังคับของบริษัทที่กำหนดและทำลาในระบบ Dingtalk เมื่อได้รับการอนุมัติแล้วจึงจะหยุดงานได้ ไม่อย่างนั้นจะถือว่าเป็นการขาดงาน\n"
            "การลากระทันหันหรือเจ็บป่วยกระทันหัน จะต้องแจ้งให้ผู้บังคับบัญชาได้ทราบโดยเร็วที่สุดเท่าที่จะทำได้ทั้งนี้ให้ทำการแจ้งภายใน 08.00 น. หรือ ภายใน 1 ชั่วโมงแรกในกะที่หยุดงาน และให้ทำลาในระบบ Dingtalk ทันที หรือในวันแรกที่กลับมาทำงาน\n"
            "การลาที่ไม่ถูกต้องตามหลักเกณฑ์ดังกล่าว หากมีการหยุดงานถือว่าพนักงานผู้นั้นขาดงาน ละทิ้งหน้าที่ จะไม่ได้รับค่าจ้างในวันดังกล่าว และมีโทษทางวินัยด้วย\n"
        )
    },
    {
        "title": "วันหยุดบริษัท ประจำปี 2568",
        "content": (
            "1 ม.ค.วันขึ้นปีใหม่\n"
            "11 ก.พ.วันมาฆบูชา\n"
            "7 เม.ย.ชดเชยวันจักรี\n"
            "13 ถึง 15 เม.ย.เทศกาลสงกรานต์\n"
            "1 พ.ค.วันแรงงานแห่งชาติ\n"
            "5 พ.ค.วันฉัตรมงคล (4 พ.ค. ตรงวันอาทิตย์)\n"
            "12 พ.ค.ชดเชยวันวิสาขบูชา\n"
            "3 มิ.ย.วันเฉลิมพระชนมพรรษา สมเด็จพระราชินีฯ\n"
            "10 ก.ค.วันอาสาฬหบูชา\n"
            "28 ก.ค.วันเฉลิมพระชนมพรรษา ร.10\n"
            "12 ส.ค.วันแม่แห่งชาติ\n"
            "13 ต.ค.วันนวมินทรมหาราช (วันคล้ายวันสวรรคต ร.9)\n"
            "23 ต.ค.วันปิยมหาราช\n"
            "10 ธ.ค.วันรัฐธรรมนูญ\n"
            "31 ธ.ค.วันสิ้นปี"
        )
    }
]


# Build context text
context_blocks = [f"{doc['title']}:\n{doc['content']}" for doc in knowledge]
context_text = "\n\n".join(context_blocks)

root_agent = Agent(
    # A unique name for the agent.
    name="one_to_all_agent",
    model="gemini-2.0-flash-exp",
    description="Agent to provide guidance and support to employees of 1-to-all Company Limited.",
    instruction=f"""
    You are the 1-to-all Agent, a helpful assistant providing guidance and recommendations to employees of 1-to-all Company Limited.
    Use the best available model to answer questions and assist employees conversationally.
    Today's date is {get_current_time()}.

    ต่อไปนี้คือข้อมูลอ้างอิงจากบริษัท:
    {context_text}

    หมายเหตุ: เมื่อต้องใส่ตัวเลข ให้เขียนเป็นคำภาษาไทยเสมอ เช่น '5' ให้ตอบว่า 'ห้า'
    โปรดตอบให้กระชับ ตรงประเด็น ไม่ยาวเกินไป ตอบเฉพาะสิ่งที่ผู้ใช้งานสอบถาม หรืออ้างอิงจากข้อมูลด้านบนเท่านั้น
    โปรดใช้เสียงที่เป็นมิตร พูดอย่างชัดเจน ไม่เล่นคำหรือเล่นสำเนียง
    โปรดตอบเป็นผู้ชาย ใช้คำลงท้ายว่า 'ครับ' เท่านั้น
    """,
    tools=[],
)


