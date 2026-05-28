# Univers Chess Bot

Univers Chess Bot - Telegram guruhlarida ikki odam o'rtasida shaxmat va shashka o'ynash uchun bot. Bot mavjud Univers Mafia profil tizimiga ulanadi: asosiy `User` va `Profile` modellari o'zgartirilmaydi, board game'lar uchun alohida profil va o'yin modellari yaratiladi.

## Asosiy Maqsad

Bot foydalanuvchilarga:

- inline mode orqali istalgan chatda do'stini shaxmat yoki shashkaga chaqirish;
- yaratuvchi rangini oldindan tanlash;
- o'yin turini va vaqt limitini xabarning o'zida tanlash;
- real shaxmat va shashka qoidalari bo'yicha yurish;
- o'yin natijasiga qarab dollar mukofoti olish;
- shaxmat va shashka statistikasi hamda reytingini yig'ish imkonini beradi.

Kompyuter bilan o'ynash rejimi bo'lmaydi. Har bir o'yin faqat 2 ta Telegram foydalanuvchisi orasida bo'ladi.

O'yin endi slash komandalar bilan emas, Telegram inline mode orqali boshlanadi. Foydalanuvchi istalgan chat inputida bot username'ini yozadi va bot 2 ta inline variant qaytaradi:

- `Oq bo'lib boshlash` - yaratuvchi oq rangda o'ynaydi;
- `Qora bo'lib boshlash` - yaratuvchi qora rangda o'ynaydi.

Variant tanlangandan keyin Telegram chatga bot xabarini joylaydi. Qolgan jarayon shu xabarning inline keyboardida davom etadi: yaratuvchi o'yin turini tanlaydi:

- shaxmat;
- shashka.

Keyin vaqt limiti tanlanadi va raqib `Qabul qilish` tugmasi bilan o'yinga kiradi. Shu yondashuv guruhlarda slash command xabarlarini kamaytiradi va Telegram limitlariga tez tushib qolish xavfini pasaytiradi. Inline xabarlar private chatlarda ham ishlaydi, shuning uchun ikki foydalanuvchi shaxsiy chatda ham o'ynashi mumkin.

BotFather'da bot uchun inline mode yoqilgan bo'lishi kerak.

## Mavjud Mafia Modellari

`models/user.py` ichidagi mavjud modellar boshqa botdan olingan va o'zgartirilmaydi.

Muhim modellar:

- `User` - Telegram foydalanuvchisi.
- `Profile` - asosiy mafia profili, dollar va olmos hisoblari shu yerda turadi.

Bot shu modellardan foydalanadi, lekin ularni buzmaydi yoki qayta tuzmaydi.

## Yangi O'yin Modellari

Shaxmat va shashka uchun alohida modellar qo'shiladi. Mavjud `User` va `Profile` modellari o'zgartirilmaydi.

### ChessProfile

Har bir `User` uchun bitta shaxmat profili.

Kerakli maydonlar:

- `user` - `User` modeliga foreign key, unique.
- `rating` - shaxmat reytingi, default masalan `1000`.
- `games_count` - jami o'yinlar soni.
- `wins` - g'alabalar soni.
- `losses` - mag'lubiyatlar soni.
- `draws` - duranglar soni.
- `created_at`.
- `updated_at`.

Bu model faqat shaxmat statistikasi uchun ishlatiladi. Dollar va olmos `Profile` modelida qoladi.

### CheckersProfile

Har bir `User` uchun bitta shashka profili.

Kerakli maydonlar:

- `user` - `User` modeliga foreign key, unique.
- `rating` - shashka reytingi, default masalan `1000`.
- `games_count` - jami o'yinlar soni.
- `wins` - g'alabalar soni.
- `losses` - mag'lubiyatlar soni.
- `draws` - duranglar soni.
- `created_at`.
- `updated_at`.

Bu model shashka statistikasi va reytingi uchun ishlatiladi. Mukofot dollari baribir asosiy `Profile.dollar`ga qo'shiladi.

### ChessGame

Har bir boshlangan shaxmat o'yini.

Kerakli maydonlar:

- `white_player` - oq dona egasi.
- `black_player` - qora dona egasi.
- `winner` - g'olib foydalanuvchi, durang yoki bekor qilingan o'yinda `null`.
- `chat_id` - o'yin qaysi chatda boshlangan.
- `chat_type` - `inline`, `private`, `group` yoki `supergroup`.
- `message_id` - oddiy bot xabari bo'lsa board turgan Telegram xabar IDsi.
- `inline_message_id` - inline mode orqali yuborilgan board xabar IDsi.
- `fen` - boardning hozirgi holati.
- `status` - `pending`, `active`, `white_won`, `black_won`, `draw`, `cancelled`, `resigned`.
- `turn` - hozir kim yurishi kerak.
- `result_reason` - `checkmate`, `resign`, `timeout`, `draw`, `stalemate`, `insufficient_material` va hokazo.
- `reward_amount` - g'olibga berilgan dollar.
- `time_control` - tanlangan vaqt: `10`, `15`, `30`, `60`.
- `white_time_left` - oq o'yinchining qolgan vaqti, sekundlarda.
- `black_time_left` - qora o'yinchining qolgan vaqti, sekundlarda.
- `last_move_at` - oxirgi yurish vaqti.
- `increment_seconds` - har yurishdan keyin qo'shiladigan vaqt.
- `started_at`.
- `finished_at`.
- `created_at`.
- `updated_at`.

### CheckersGame

Har bir boshlangan shashka o'yini.

Kerakli maydonlar `ChessGame`ga o'xshash bo'ladi:

- `white_player`.
- `black_player`.
- `winner`.
- `chat_id`.
- `chat_type`.
- `message_id`.
- `inline_message_id`.
- `board_state` - shashka boardining hozirgi holati.
- `status` - `pending`, `active`, `white_won`, `black_won`, `draw`, `cancelled`, `resigned`.
- `turn`.
- `result_reason` - `capture_all`, `blocked`, `resign`, `timeout`, `draw` va hokazo.
- `reward_amount`.
- `time_control`.
- `white_time_left`.
- `black_time_left`.
- `last_move_at`.
- `increment_seconds`.
- `started_at`.
- `finished_at`.
- `created_at`.
- `updated_at`.

### ChessMove

O'yindagi yurishlar tarixi.

Kerakli maydonlar:

- `game` - `ChessGame`ga foreign key.
- `player` - yurish qilgan `User`.
- `move_number`.
- `from_square` - masalan `e2`.
- `to_square` - masalan `e4`.
- `promotion` - farzin/ruh/fil/otga aylanish kerak bo'lsa.
- `san` - shaxmat notatsiyasi, masalan `Nf3`, `Qxe7#`.
- `fen_after` - yurishdan keyingi holat.
- `created_at`.

### CheckersMove

Shashkadagi yurishlar tarixi.

Kerakli maydonlar:

- `game` - `CheckersGame`ga foreign key.
- `player` - yurish qilgan `User`.
- `move_number`.
- `from_square`.
- `to_square`.
- `captured_squares` - urib olingan donalar ro'yxati.
- `became_king` - damkaga aylangan bo'lsa.
- `board_after` - yurishdan keyingi board holati.
- `created_at`.

## O'yin Flow

### Inline Mode Orqali O'yin Boshlash

1. Foydalanuvchi istalgan Telegram chat inputida bot username'ini yozadi.
2. Bot inline queryga 2 ta result qaytaradi: `Oq bo'lib boshlash` va `Qora bo'lib boshlash`.
3. Foydalanuvchi bitta resultni tanlaydi va Telegram tanlangan resultni chatga xabar sifatida joylaydi.
4. Joylangan xabarda yaratuvchi `Shaxmat` yoki `Shashka`ni tanlaydi.
5. Bot shu xabarni edit qilib vaqt limitlarini chiqaradi: `10`, `15`, `30`, `60`.
6. Yaratuvchi vaqt limitini tanlaydi.
7. Bot shu xabarni challenge holatiga edit qiladi.
8. Ikkinchi foydalanuvchi `Qabul qilish` tugmasini bosadi.
9. Tanlangan rangga qarab oq va qora o'yinchilar aniqlanadi.
10. Tanlangan turga qarab `ChessGame` yoki `CheckersGame` yaratiladi.
11. Board doim bitta inline xabarda qoladi, har yurishda shu xabar edit qilinadi.
12. Board ostida action tugmalar turadi: taslim bo'lish va durang taklif qilish.

Inline xabarlarda Telegram callbacklari `chat_id/message_id` o'rniga `inline_message_id` beradi. Shu sabab `ChessGame` va `CheckersGame` modellarida `inline_message_id` maydoni bor. Inline o'yinlarda `chat_id=0`, `chat_type=inline`, `message_id=null` bo'ladi; oddiy bot xabari orqali yaratilgan eski o'yinlarda esa `chat_id/message_id` ishlatiladi.

`/chesswhite`, `/chessblack` va `/chessbalck` komandalaridan yangi challenge yaratilmaydi. Ular foydalanuvchini inline mode orqali boshlashga yo'naltiradi.

### Yurish Qilish

1. Navbati kelgan o'yinchi o'z donasini bosadi.
2. Bot legal yurishlarni belgilaydi.
3. O'yinchi boradigan katakni bosadi.
4. Bot o'yin turiga qarab yurish legal ekanini tekshiradi.
5. Shaxmatda FEN, shashkada `board_state` yangilanadi.
6. O'yinchining qolgan vaqti hisoblanadi.
7. Agar yurish vaqtida qilingan bo'lsa, har yurishdan keyin `increment_seconds` qo'shiladi.
8. Board Telegram xabarida edit qilinadi.
9. Navbat ikkinchi o'yinchiga o'tadi.

### Board Ostidagi Tugmalar

Har bir active o'yin boardi ostida doimiy action tugmalar bo'ladi:

- taslim bo'lish tugmasi;
- durang taklif qilish tugmasi.

Bu ishlar alohida command bilan qilinmaydi. Foydalanuvchi board ostidagi tugmani bosadi.

Taslim bo'lish:

1. O'yinchi taslim bo'lish tugmasini bosadi.
2. Bot tasdiqlash uchun emojili tugmalar chiqaradi.
3. O'yinchi tasdiqlasa, raqib g'olib bo'ladi.
4. Board xabari yangilanadi va g'olib tugmalarda ham aks etadi.

Durang taklif qilish:

1. O'yinchi durang taklif qilish tugmasini bosadi.
2. Bot board ostida raqib uchun emojili `true/false` tanlovini chiqaradi.
3. Faqat raqib javob bera oladi.
4. Raqib `true` tanlasa, o'yin durang bilan tugaydi.
5. Raqib `false` tanlasa, o'yin davom etadi va oddiy action tugmalar qaytadi.

O'yin tugagandan keyin board ostidagi tugmalar ham natijani ko'rsatadi:

- oq g'olib bo'lsa, oq tomonga g'alaba belgisi;
- qora g'olib bo'lsa, qora tomonga g'alaba belgisi;
- durang bo'lsa, durang belgisi;
- timeout, resign yoki checkmate sababi qisqa aks etadi.

### Vaqt Limiti

O'yin boshida yaratuvchi quyidagi vaqt limitlaridan birini tanlaydi:

- `10` daqiqa;
- `15` daqiqa;
- `30` daqiqa;
- `60` daqiqa.

Har bir o'yinchida alohida vaqt bo'ladi. Navbat kimda bo'lsa, faqat o'sha o'yinchining vaqti kamayadi.

Vaqt ishlash tartibi:

1. O'yin boshlanganda har ikki o'yinchiga tanlangan vaqt sekundlarda beriladi.
2. Har yurishda `now - last_move_at` hisoblanib, navbatdagi o'yinchining vaqtidan ayriladi.
3. Yurish muvaffaqiyatli bo'lsa, o'sha o'yinchiga `increment_seconds` qo'shiladi.
4. Vaqti `0` bo'lgan o'yinchi timeout bilan yutqazadi.

Boshlang'ich increment taklifi:

```text
10 daqiqa -> +5 sekund
15 daqiqa -> +10 sekund
30 daqiqa -> +20 sekund
60 daqiqa -> +30 sekund
```

Bu Fischer increment uslubiga o'xshaydi: tez yurish qilgan o'yinchi vaqtini yaxshiroq saqlab qoladi, har yurishdan keyin esa ozgina vaqt qo'shib oladi.

### O'yin Tugashi

O'yin quyidagi holatlarda tugaydi:

- checkmate yoki shashkada raqib donalarini yutib tugatish;
- resign;
- draw;
- stalemate;
- insufficient material;
- timeout.

O'yin tugaganda:

1. O'yin statusi va `result_reason` yangilanadi.
2. O'yin turiga qarab `ChessProfile` yoki `CheckersProfile` statistikasi yangilanadi.
3. Reyting qayta hisoblanadi.
4. G'olibga 10 dan 100 dollargacha mukofot beriladi.
5. Mukofot asosiy `Profile.dollar` maydoniga qo'shiladi.

## Mukofot Tizimi

G'olibga beriladigan mukofot 10-100 dollar oralig'ida bo'ladi.

Boshlang'ich formula:

- Oddiy g'alaba: `30$`
- Checkmate bilan g'alaba: `50$`
- Kuchliroq raqibni yutish: bonus
- Tez g'alaba: bonus
- Uzoq va to'liq o'yin: bonus
- Raqib resign qilsa: `20$`
- Juda qisqa resign yoki bekor qilish: mukofot berilmaydi

Tavsiya qilingan hisoblash:

```text
base = 30
checkmate_bonus = 20
rating_bonus = 0..30
move_quality_bonus = 0..20
reward = min(100, max(10, base + bonuses))
```

Mukofot faqat g'olibga beriladi. Durangda dollar berilmaydi.

## Reyting Tizimi

ChessProfile va CheckersProfile uchun oddiy Elo uslubidagi alohida reyting ishlatiladi.

Boshlang'ich reyting:

```text
1000
```

G'alabada:

- kuchsizroq raqibni yutsa kamroq reyting;
- kuchliroq raqibni yutsa ko'proq reyting;
- yutqazgan odamdan reyting ayriladi;
- durangda kuchliroq reytingli odam ozgina yo'qotishi, pastroq reytingli odam ozgina olishi mumkin.

Keyinchalik shaxmat va shashka uchun alohida leaderboard qilinadi.

## Callback Data Rejasi

Inline tugmalar callbacklari qisqa va aniq bo'lishi kerak.

Misollar:

```text
bg:type:<challenge_id>:chess
bg:type:<challenge_id>:checkers
bg:time:<challenge_id>:10
bg:accept:<game_type>:<game_id>
bg:cancel:<game_type>:<game_id>
bg:sel:<game_type>:<game_id>:e2
bg:move:<game_type>:<game_id>:e2:e4
bg:resign:<game_type>:<game_id>
bg:resign_yes:<game_type>:<game_id>
bg:resign_no:<game_type>:<game_id>
bg:draw:<game_type>:<game_id>
bg:draw_yes:<game_type>:<game_id>
bg:draw_no:<game_type>:<game_id>
```

Har bir callbackda tekshiriladi:

- o'yin mavjudmi;
- status `active`mi;
- bosgan odam shu o'yinchilardan birimi;
- hozir uning navbatimi;
- yurish legalmi.
- durangga faqat raqib javob beryaptimi;
- taslim bo'lishni faqat tugmani bosgan o'yinchining o'zi tasdiqlayaptimi.

## Board Render Rejasi

Board qo'lda 64 ta button yozilmaydi. Har bir o'yin turi uchun render funksiyasi board yaratadi.

Shaxmat render vazifalari:

- FENdan board o'qish;
- 8x8 inline keyboard yaratish;
- oq va qora donalarni custom emoji bilan chiqarish;
- bo'sh kataklarni rangli button sifatida ko'rsatish;
- tanlangan dona va legal yurishlarni alohida ko'rsatish;
- oq/qora tomonga qarab board orientatsiyasini sozlash.
- board ostiga taslim bo'lish va durang taklif qilish tugmalarini qo'shish.

Shashka render vazifalari:

- `board_state`dan board o'qish;
- 8x8 inline keyboard yaratish;
- oddiy dona va damkalarni alohida ko'rsatish;
- urish majburiy bo'lsa, faqat legal urishlarni ko'rsatish;
- ko'p martalik urish davom etsa, o'sha dona bilan yurishni davom ettirish;
- oq/qora tomonga qarab board orientatsiyasini sozlash.
- board ostiga taslim bo'lish va durang taklif qilish tugmalarini qo'shish.

## Kerakli Kutubxonalar

Asosiy kutubxonalar:

- `aiogram` - Telegram bot.
- `tortoise-orm` - database ORM.
- `python-chess` - shaxmat qoidalari va yurish validatsiyasi.
- `python-dotenv` - `.env` orqali sozlamalar.

`python-chess` majburiy bo'ladi, chunki shaxmat qoidalarini qo'lda yozish xato ehtimolini juda oshiradi.

Shashka uchun mos tayyor kutubxona topilsa ishlatiladi. Agar loyiha talabiga mos ishonchli kutubxona topilmasa, shashka qoidalari alohida service modulida yoziladi va testlar bilan qoplanadi.

## Minimal Ish Rejasi

1. `models/__init__.py` import xatosini tuzatish.
2. Bot startida DB init qilish.
3. `ChessProfile`, `ChessGame`, `ChessMove` modellarini qo'shish.
4. `CheckersProfile`, `CheckersGame`, `CheckersMove` modellarini qo'shish.
5. `python-chess`ni dependency sifatida qo'shish.
6. Shashka qoidalari uchun service yoki kutubxona tanlash.
7. Board render funksiyalarini yozish.
8. Inline query handlerini yozish.
9. Inline resultlarda oq/qora bo'lib boshlash variantlarini qaytarish.
10. O'yin turi tanlash flowini yozish.
11. Vaqt limiti tanlash flowini yozish.
12. Inline xabar uchun challenge/accept flow yozish.
13. Yurish tanlash va legal move flow yozish.
14. Board ostidagi taslim bo'lish va durang taklif qilish tugmalarini yozish.
15. Durang taklifiga raqib `true/false` javob beradigan flow yozish.
16. Vaqt hisoblash va timeout flowini yozish.
17. Game over holatlarini qayta ishlash.
18. ChessProfile va CheckersProfile statistikalarini yangilash.
19. Asosiy `Profile.dollar` hisobiga mukofot qo'shish.
20. Reyting formulasini ulash.
21. Leaderboard va profil komandalarini qo'shish.

## Komandalar

Bot komandalar:

- `/start` - bot haqida qisqa xabar.
- `/profile` - profil va shaxmat/shashka statistikasi.
- `/top` - reyting bo'yicha TOP.

Legacy komandalar:

- `/chesswhite`, `/chessblack`, `/chessbalck` - yangi challenge yaratmaydi, foydalanuvchini inline mode orqali boshlashga yo'naltiradi.

## Muhim Qoidalar

- `User` va asosiy `Profile` model strukturasi o'zgartirilmaydi.
- Dollar mukofoti faqat asosiy `Profile.dollar`ga yoziladi.
- ChessProfile faqat shaxmat statistikasi va reyting uchun ishlatiladi.
- CheckersProfile faqat shashka statistikasi va reyting uchun ishlatiladi.
- Har bir yurish server tomonda tekshiriladi.
- Faqat navbati kelgan o'yinchi yurishi mumkin.
- O'yinchi o'ziga qarshi o'yin boshlay olmaydi.
- Botlar bilan o'yin boshlash taqiqlanadi.
- Bir foydalanuvchi bir vaqtning o'zida umumiy hisobda maksimal 2 ta active o'yinda qatnasha oladi.
- Durangda dollar mukofoti berilmaydi.
- O'yin boshida vaqt limiti majburiy tanlanadi.
- Board doim bitta inline xabarda qoladi.
- Taslim bo'lish va durang taklif qilish command orqali emas, board ostidagi tugmalar orqali ishlaydi.
- Durang taklifiga faqat raqib javob bera oladi.
- Inline mode yoqilgan bo'lishi shart.

## Keyingi Qarorlar

Quyidagi narsalar keyinroq aniqlanadi:

- shashka uchun qaysi qoida varianti ishlatiladi;
- vaqt increment qiymatlari hozirgi taklifda qoladimi yoki sozlanadimi.
