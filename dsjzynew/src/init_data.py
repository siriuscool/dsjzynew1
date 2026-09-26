from src.database import get_conn

def init_sample_data():
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM cadets")
    if c.fetchone()[0] > 0:
        conn.close()
        print("已有数据，跳过")
        return

    platoons = ["一派", "二派", "三派"]
    classes = ["一b","二b","三b","四b","五b","六b","七b","八b","九b"]
    cadets_per_class = 8

    surnames = list("张王李刘陈杨赵孙周吴郑冯蒋沈韩朱秦许何吕施孔曹严华金魏陶姜戚谢邹喻柏水窦章云苏潘葛奚范彭郎鲁韦昌马苗凤花方俞任袁柳鲍史唐费廉岑薛雷贺倪汤滕殷罗毕郝安常乐于时傅齐")
    given_names = list("伟强娜洋静帆磊悦涛敏浩芳明丽勇晨波静鹏敏军磊洋婷鑫宇欣怡哲琪轩然杰琳超雪峰梦刚瑶毅萱健萍俊燕辉红凯霞亮梅斌兰龙竹飞菊鹏荷丹阳青帆蓝文紫武翠斌玉辰蓉泽婉霖瑾豪蕾睿")

    cadet_id = 1

    # 脸部4人
    for role in ["联长", "知道猿", "副联长", "副知道猿"]:
        name = surnames[(cadet_id-1) % len(surnames)] + given_names[(cadet_id-1) % len(given_names)]
        c.execute("INSERT INTO cadets (name,student_id,platoon,class_name,role,phone) VALUES (?,?,?,?,?,?)",
                  (name, f"2024{cadet_id:03d}", "脸部", "脸部", role, f"138{cadet_id:08d}"))
        cadet_id += 1

    # 3个派，每派3个b，每b 8人
    class_idx = 0
    for platoon in platoons:
        # 派长1人
        name = surnames[(cadet_id-1) % len(surnames)] + given_names[(cadet_id-1) % len(given_names)]
        c.execute("INSERT INTO cadets (name,student_id,platoon,class_name,role,phone) VALUES (?,?,?,?,?,?)",
                  (name, f"2024{cadet_id:03d}", platoon, "派长", "派长", f"138{cadet_id:08d}"))
        cadet_id += 1

        for _ in range(3):
            cls = classes[class_idx]
            class_idx += 1
            for i in range(cadets_per_class):
                name = surnames[(cadet_id-1) % len(surnames)] + given_names[(cadet_id-1) % len(given_names)]
                if i == 0: role = "搬涨"
                elif i == 1: role = "副搬涨"
                else: role = "学员"
                c.execute("INSERT INTO cadets (name,student_id,platoon,class_name,role,phone) VALUES (?,?,?,?,?,?)",
                          (name, f"2024{cadet_id:03d}", platoon, cls, role, f"138{cadet_id:08d}"))
                cadet_id += 1

    conn.commit()
    conn.close()
    print(f"已初始化 {cadet_id-1} 名人员（脸部4 + 派长3 + 9个b x 8人）")
