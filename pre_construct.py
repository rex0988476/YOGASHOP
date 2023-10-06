import mysql.connector
connection = mysql.connector.connect(host='localhost',#創建連線
                                    port='3306',
                                    user='root',
                                    password='hsieh17')
#                                   database='database_system' ) #可先預設要使用的資料庫

cursor = connection.cursor()#開始使用
#DROP DATABASE `database_system`;
cursor.execute("DROP DATABASE `database_system`;")
#create db
cursor.execute("CREATE DATABASE `database_system`;")

#use
cursor.execute("USE `database_system`;")

#create table
cursor.execute("CREATE TABLE `member`(`member_id` VARCHAR(20) PRIMARY KEY,`password` VARCHAR(20) NOT NULL,`name` VARCHAR(12) NOT NULL,`picture` VARCHAR(40),`phone_number` VARCHAR(10) NOT NULL,`bank_account` VARCHAR(20) DEFAULT NULL,`credit card` VARCHAR(20) DEFAULT NULL,`manager_id` VARCHAR(20) NOT NULL);")
cursor.execute("CREATE TABLE `consult`(`consult_id` INTEGER NOT NULL,`sender_id` VARCHAR(20) NOT NULL,`receive_id` VARCHAR(20) NOT NULL,`consult_record` VARCHAR(100) NOT NULL,`consult_time` TIMESTAMP NOT NULL,PRIMARY KEY(`consult_id`));")
cursor.execute("CREATE TABLE `goods`(`member_id` VARCHAR(20) NOT NULL,`goods_id` INTEGER NOT NULL,`goods_name` VARCHAR(20) NOT NULL,`goods_picture` VARCHAR(40),`goods_describe` VARCHAR(100) NOT NULL,`goods_author` VARCHAR(20) NOT NULL,`goods_price` INTEGER NOT NULL,`goods_quantity` INTEGER NOT NULL,`goods_dates` DATE NOT NULL,`goods_rate` FLOAT NOT NULL DEFAULT -1,`supply_status` INTEGER NOT NULL DEFAULT 1,`can_bid` INTEGER NOT NULL DEFAULT 0,PRIMARY KEY(`member_id`,`goods_id`));")
cursor.execute("CREATE INDEX `goods_id` ON `goods` (`goods_id`);")
cursor.execute("CREATE INDEX `goods_name` ON `goods` (`goods_name`);")
cursor.execute("CREATE TABLE `goods_CD`(`goods_CD_id` INTEGER NOT NULL,`category` VARCHAR(20) NOT NULL,PRIMARY KEY(`goods_CD_id`,`category`));")
cursor.execute("CREATE TABLE `goods_book`(`goods_book_id` INTEGER PRIMARY KEY,`goods_book_publisher` VARCHAR(20) NOT NULL);")
cursor.execute("CREATE TABLE `goods_book_category`(`goods_book_id` INTEGER NOT NULL,`category` VARCHAR(20) NOT NULL,PRIMARY KEY(`goods_book_id`,`category`));")
cursor.execute("CREATE TABLE `transaction_record` (`member_id` VARCHAR(20) NOT NULL,`transaction_id` INTEGER  NOT NULL,`buy_date` TIMESTAMP  NOT NULL,`arrival_date` TIMESTAMP,`finish_date` TIMESTAMP DEFAULT NULL,`total_price` INTEGER  NOT NULL,`transaction_status` INTEGER NOT NULL DEFAULT 0,PRIMARY KEY(`member_id`,`transaction_id`));")
cursor.execute("CREATE INDEX `transaction_id` ON `transaction_record` (`transaction_id`);")
cursor.execute("CREATE TABLE `shopping_cart`(`member_id` VARCHAR(20) NOT NULL,`goods_id` INTEGER  NOT NULL,`goods_name` VARCHAR(20)   NOT NULL,`goods_price` INTEGER,`goods_picture` VARCHAR(40),`goods_amount` INTEGER  NOT NULL,PRIMARY KEY(`member_id`,`goods_id`));")
cursor.execute("CREATE INDEX `goods_price` ON `shopping_cart` (`goods_price`);")
cursor.execute("CREATE INDEX `goods_amount` ON `shopping_cart` (`goods_amount`);")
cursor.execute("CREATE TABLE `transaction_record_goods`(`transaction_id` INTEGER  NOT NULL,`goods_id` INTEGER  NOT NULL,`goods_name` VARCHAR(20)  NOT NULL,`goods_price` INTEGER   NOT NULL,`goods_amount` INTEGER   NOT NULL,`goods_status` INTEGER NOT NULL DEFAULT 0,PRIMARY KEY(`transaction_id`,`goods_id`));")
cursor.execute("CREATE TABLE `buy`(`member_id` VARCHAR(20) NOT NULL,`goods_id`      INTEGER  NOT NULL,`transaction_id` INTEGER  NOT NULL,`star_rate` INTEGER NOT NULL DEFAULT -1,`rate`        VARCHAR(100) DEFAULT NULL,PRIMARY KEY(`member_id`,`goods_id`,`transaction_id`));")
cursor.execute("CREATE TABLE `report`(`member_id` VARCHAR(20) NOT NULL,`seller_id` VARCHAR(20) NOT NULL,`report_text` VARCHAR(100) DEFAULT NULL,PRIMARY KEY(`member_id`,`seller_id`));")
cursor.execute("CREATE TABLE `QA`(`QA_id` VARCHAR(4) NOT NULL,`Q` VARCHAR(100) NOT NULL,`A` VARCHAR(100) NOT NULL,PRIMARY KEY(`QA_id`));")
cursor.execute("CREATE TABLE `bid`(`bid_id` INTEGER NOT NULL,`bid_goods_id` INTEGER NOT NULL,`max_price` INTEGER NOT NULL,`max_member_id` VARCHAR(20) DEFAULT NULL,`start_date` TIMESTAMP NOT NULL,`end_date` TIMESTAMP NOT NULL,`bid_status` VARCHAR(3) NOT NULL DEFAULT '0',PRIMARY KEY(`bid_id`));")
cursor.execute("CREATE TABLE `manual`(`id` INTEGER NOT NULL DEFAULT 0,`text` VARCHAR(1000) DEFAULT NULL,PRIMARY KEY(`id`));")


#pre insert
cursor.execute("insert into `manual` values(0,'我是使用手冊');")

cursor.execute("insert into `member` values('000000','yoga7414','000000','000000.jpg','0000000000','00000000000000','0000000000000000','000000');")
cursor.execute("insert into `member` values('pekora000','pekora000','pekora','pekora000_avatar.jpg','0912345678','12345678901234','1234567890123456','000000');")
cursor.execute("insert into `member` values('watame000','watame000','watame','watame000_avatar.jpg','0923456789','23456789012345','1234567890123456','000000');")
cursor.execute("insert into `member` values('nezuko000','nezuko000','nezuko','nezuko000_avatar.jpg','0934567890','34567890123456','1234567890123456','000000');")
cursor.execute("insert into `member` values('smilecat000','smilecat000','cat','smilecat000_avatar.jpg','0945678901','45678901234567','1234567890123456','000000');")
cursor.execute("insert into `member` values('stupiddog000','stupiddog000','dog','stupiddog000_avatar.jpg','0956789012','56789012345678','1234567890123456','000000');")

#書編號從1004開始往後+1
#CD編號從2001開始往後+1
#商品圖片檔名=商品編號+副檔名
#商品狀態有:全新,9成新,5成新,3成新
#日期格式:yyyy-mm-dd
#評價為浮點數,要加小數點
#價錢請<2000
#格式
#cursor.execute("insert into `goods` values('賣家id',商品編號,'商品名稱','商品圖片檔名','商品敘述','作者名稱',價錢,數量,'日期',評價,'商品狀態',1);")
cursor.execute("insert into `goods` values('pekora000',1001,'系統分析與設計:使用UML','1001.jpg','本書讓學生把焦點放在進行SAD,提供我們認為現在及未來每位分析師必須知道的核心技能,從而捕捉該領域的動態面貌,並建立在我們從事系統分析的專業經驗以及SAD教學的基礎上.','林冠成,王裕華',620,10,'2022-04-30',-1,1,1);")
cursor.execute("insert into `goods` values('pekora000',1002,'資料庫系統第7版','1002.jpg','本書介紹了設計、使用和實現數據庫系統和數據庫應用程序所必需的基本概念。 我們的演講強調數據庫建模和設計的基礎、數據庫管理系統提供的語言和模型以及數據庫系統實現技術。','Elmasri,Navathe',1000,10,'2022-04-29',-1,1,1);")
cursor.execute("insert into `goods` values('smilecat000',1003,'紫羅蘭永恆花園','1003.jpg','《紫羅蘭永恆花園》（ヴァイオレット・エヴァーガーデン）為日本輕小說作品,插畫由高瀨亞貴子所繪製,由KA Esuma文庫出版、發行。獲得第5屆京都動畫大獎,也是該比賽舉辦以來,目前唯一獲得大賞獎的作品。','曉佳奈',350,3,'2022-04-28',-1,1,1);")
cursor.execute("insert into `goods` values('nezuko000',1004,'（日本版漫畫）天氣之子 3','1004.jpg','《你的名字。》導演．新海誠最新作品日本年度最賣座電影――天氣之子漫畫版堂堂完結！！！','新海誠',200,3,'2022-05-01',-1,1,1);")
cursor.execute("insert into `goods` values('stupiddog000',2001,'五月天 / 神的孩子都在跳舞','2001.jpg','當我和世界不一樣 那就讓我不一樣史上第5張五月天 MAYDAY 2004最新專輯5th album,絕對要推薦！','五月天 MayDay',520,2,'2022-05-01',-1,1,1);")
cursor.execute("insert into `goods` values('stupiddog000',2002,'夏川里美 /《明日的搖籃曲》','2002.jpg','繼〈淚光閃閃〉〈童神〉後，夏川里美全新單曲代表作！〈島歌〉原唱THE BOOM宮澤和史力挺跨刀製作','夏川里美 Natshukawa Rimi',189,3,'2022-04-29',-1,1,1);")
cursor.execute("insert into `goods` values('watame000',2003,'西洋老式情歌 (10CD)','2003.jpg','迷人巨星千萬風采 一生難忘的經典感動膾炙人口西洋情歌 走過跨世紀精華路程歷年佳作一次收錄 原曲原唱重回往日情懷,值得珍藏的不朽情歌 一次擁有愛情的各種滋味','合輯',198,1,'2022-04-28',-1,1,1);")
cursor.execute("insert into `goods` values('nezuko000',2004,'三個傻瓜 (藍光BD)','2004.jpg','迷幽默省思教育意義，年度最具啟發性的溫馨爆笑電影！','vinod chopra',800,2,'2022-04-26',-1,1,1);")
cursor.execute("insert into `goods` values('watame000',1005,'埃及守護神1：紅色金字塔','1005.jpg','全球暢銷【珀西·傑克遜】作者瑞克·里奧丹最新力作！繼【珀西·傑克遜】之後，瑞頓延續了他出色的講故事能力，創造了另一個不同主角、人物、神話和場景的迷人埃及奇幻世界！','Rick Riordan',360,3,'2022-05-03',-1,1,1);")
cursor.execute("insert into `goods` values('pekora000',1006,'享受吧！一個人的旅行','1006.jpg','108則享樂與平衡的故事享受人生　體驗人生　熱愛人生','Elizabeth Gilbert',324,2,'2022-05-03',-1,1,1);")
cursor.execute("insert into `goods` values('smilecat000',2005,'怪獸與葛林戴華德的罪行','2005.jpg','J.K.羅琳魔法世界全新冒險五部曲中的第二部大作','大衛．葉慈',880,1,'2022-04-30',-1,1,1);")
cursor.execute("insert into `goods` values('smilecat000',1007,'刺蝟的優雅','1007.jpg','最巴黎、最優雅的小說，魅力無可抗拒！就算是鐵石心腸，你也會為她激動!法國書商一致推薦的「極品小說」！','Muriel Barbery',350,5,'2022-04-28',-1,1,1);")
cursor.execute("insert into `goods` values('pekora000',1008,'少年鱷魚幫','1008.jpg','　一個廢棄工廠、一樁懸疑竊盜案，還有一幫「鱷魚幫」少年，將展開史上最驚險刺激的大冒險！熱血+義氣+冒險=少年鱷魚幫  英雄出少年！有膽來入幫！','Max von der Grun',198,7,'2022-04-28',-1,1,1);")
cursor.execute("insert into `goods` values('stupiddog000',2006,'紫羅蘭永恆花園電影版 DVD','2006.jpg','薇爾莉特伊芙加登。在人們傷痕累累的戰爭結束後，，世界逐漸恢復平穩，生活並隨著新技術開發而改變。就在讓人們開始往前邁進之時，心懷思念重要之人的薇爾莉特，卻必須在沒有「那個人」的世界中活著。直到某天…','曉佳奈',600,5,'2022-05-01',-1,1,1);")
cursor.execute("insert into `goods` values('stupiddog000',2007,'龍貓DVD','2007.jpg','念小學的小月和四歲的妹妹小梅，跟著爸爸搬到郊外的一間舊屋住，她們的生活有了許多有趣的新發現，包括傳說中的龍貓...。有天，想媽媽的小梅決定去醫院探望她，卻在途中迷路了，大龍貓會出現幫助小月找回小梅嗎？','宮崎駿',349,4,'2022-05-02',-1,1,1);")
cursor.execute("insert into `goods` values('smilecat000',2008,'平昌冬季奧運 DVD','2008.jpg','真實記錄了奧運歷史中最具吸引力的故事！一個不受全世界關注的城市—江原道平昌市。儘管首次申辦2018冬季奧運會失敗，仍在2011年7月克服了三項挑戰。','鴻影多媒體',320,2,'2022-05-01',-1,1,1);")
cursor.execute("insert into `goods` values('nezuko000',2009,'爵士傳奇: 現代爵士四重奏 (2DVD)','2009.jpg','現代爵士四重奏成立於1952年，可說是爵士史上最長壽的團體之一。現代爵士四重奏的演奏受到古典、酷派爵士、藍調爵士與咆勃爵士影響。','現代爵士四重奏',1035,1,'2022-04-27',-1,1,1);")
cursor.execute("insert into `goods` values('nezuko000',1009,'社會系統：一個一般理論的大綱','1009.jpg','魯曼：「我的風格甚至是反諷式的。我想藉此告訴人們，請不要太認真對待我，或請不要太快地理解我。','Niklas Luhmann',625,3,'2022-04-30',-1,1,1);")


#CD分類格式
#cursor.execute("insert into `goods_CD` values(商品編號,'分類名稱');")
cursor.execute("insert into `goods_CD` values(2001,'流行');")
cursor.execute("insert into `goods_CD` values(2001,'搖滾');")
cursor.execute("insert into `goods_CD` values(2002,'民謠');")
cursor.execute("insert into `goods_CD` values(2003,'古典');")
cursor.execute("insert into `goods_CD` values(2004,'幽默喜劇');")
cursor.execute("insert into `goods_CD` values(2005,'動作冒險');")
cursor.execute("insert into `goods_CD` values(2005,'奇幻/科幻');")
cursor.execute("insert into `goods_CD` values(2005,'驚悚/恐怖');")
cursor.execute("insert into `goods_CD` values(2006,'動漫');")
cursor.execute("insert into `goods_CD` values(2006,'浪漫愛情');")
cursor.execute("insert into `goods_CD` values(2007,'動漫');")
cursor.execute("insert into `goods_CD` values(2007,'幽默喜劇');")
cursor.execute("insert into `goods_CD` values(2007,'奇幻/科幻');")
cursor.execute("insert into `goods_CD` values(2008,'紀錄片');")
cursor.execute("insert into `goods_CD` values(2009,'爵士');")





#書出版社格式
#cursor.execute("insert into `goods_book` values(商品編號,'出版社名稱');")
cursor.execute("insert into `goods_book` values(1001,'全華圖書');")
cursor.execute("insert into `goods_book` values(1002,'pearson');")
cursor.execute("insert into `goods_book` values(1003,'KA Esuma');")
cursor.execute("insert into `goods_book` values(1004,'尖端');")
cursor.execute("insert into `goods_book` values(1005,'HYPERION BOOKS');")
cursor.execute("insert into `goods_book` values(1006,'馬可孛羅');")
cursor.execute("insert into `goods_book` values(1007,'商周出版');")
cursor.execute("insert into `goods_book` values(1008,'親子天下');")
cursor.execute("insert into `goods_book` values(1009,'暖暖書屋');")



#書分類格式
#cursor.execute("insert into `goods_book_category` values(商品編號,'分類名稱');")
cursor.execute("insert into `goods_book_category` values(1001,'教科書');")
cursor.execute("insert into `goods_book_category` values(1002,'教科書');")
cursor.execute("insert into `goods_book_category` values(1003,'輕小說');")
cursor.execute("insert into `goods_book_category` values(1004,'漫畫');")
cursor.execute("insert into `goods_book_category` values(1005,'青少年文學');")
cursor.execute("insert into `goods_book_category` values(1006,'旅遊');")
cursor.execute("insert into `goods_book_category` values(1007,'文學小說');")
cursor.execute("insert into `goods_book_category` values(1008,'青少年文學');")
cursor.execute("insert into `goods_book_category` values(1009,'社會科學');")


#set foreign key
cursor.execute("ALTER TABLE `consult` ADD foreign key (`sender_id`) references `member`(`member_id`) ON DELETE CASCADE ON UPDATE CASCADE;")
cursor.execute("ALTER TABLE `consult` ADD foreign key (`receive_id`) references `member`(`member_id`) ON DELETE CASCADE ON UPDATE CASCADE;")
cursor.execute("ALTER TABLE `goods` ADD foreign key (`member_id`) references `member`(`member_id`) ON DELETE CASCADE ON UPDATE CASCADE;")
cursor.execute("ALTER TABLE `goods_CD` ADD foreign key (`goods_CD_id`) references `goods`(`goods_id`) ON DELETE CASCADE ON UPDATE CASCADE;")
cursor.execute("ALTER TABLE `goods_book` ADD foreign key (`goods_book_id`) references `goods`(`goods_id`) ON DELETE CASCADE ON UPDATE CASCADE;")
cursor.execute("ALTER TABLE `goods_book_category` ADD foreign key (`goods_book_id`) references `goods`(`goods_id`) ON DELETE CASCADE ON UPDATE CASCADE;")
cursor.execute("ALTER TABLE `transaction_record` ADD  foreign key (`member_id`) references `member`(`member_id`) ON DELETE CASCADE ON UPDATE CASCADE;")
cursor.execute("ALTER TABLE `shopping_cart` ADD  foreign key (`member_id`) references `member`(`member_id`) ON DELETE CASCADE ON UPDATE CASCADE;")
cursor.execute("ALTER TABLE `shopping_cart` ADD  foreign key (`goods_id`) references`goods`(`goods_id`) ON DELETE CASCADE ON UPDATE CASCADE;")
cursor.execute("ALTER TABLE `shopping_cart` ADD  foreign key (`goods_name`) references`goods`(`goods_name`) ON DELETE CASCADE ON UPDATE CASCADE;")
cursor.execute("ALTER TABLE `transaction_record_goods` ADD  foreign key (`transaction_id`) references`transaction_record`(`transaction_id`) ON DELETE CASCADE ON UPDATE CASCADE;")
cursor.execute("ALTER TABLE `transaction_record_goods` ADD  foreign key (`goods_id`) references`goods`(`goods_id`) ON DELETE CASCADE ON UPDATE CASCADE;")
cursor.execute("ALTER TABLE `transaction_record_goods` ADD  foreign key (`goods_name`) references`goods`(`goods_name`) ON DELETE CASCADE ON UPDATE CASCADE;")
cursor.execute("ALTER TABLE `buy` ADD  foreign key (`member_id`) references`member`(`member_id`) ON DELETE CASCADE ON UPDATE CASCADE;")
cursor.execute("ALTER TABLE `buy` ADD  foreign key (`goods_id`) references`goods`(`goods_id`) ON DELETE CASCADE ON UPDATE CASCADE;")
cursor.execute("ALTER TABLE `buy` ADD  foreign key (`transaction_id`) references`transaction_record`(`transaction_id`) ON DELETE CASCADE ON UPDATE CASCADE;")
cursor.execute("ALTER TABLE `report` ADD foreign key (`member_id`) references `member`(`member_id`) ON DELETE CASCADE ON UPDATE CASCADE;")
cursor.execute("ALTER TABLE `report` ADD foreign key (`seller_id`) references `member`(`member_id`) ON DELETE CASCADE ON UPDATE CASCADE;")
cursor.execute("ALTER TABLE `bid` ADD foreign key (`max_member_id`) references `member`(`member_id`) ON DELETE CASCADE ON UPDATE CASCADE;")
cursor.execute("ALTER TABLE `bid` ADD foreign key (`bid_goods_id`) references `goods`(`goods_id`) ON DELETE CASCADE ON UPDATE CASCADE;")


cursor.close() 
connection.commit()
connection.close()
