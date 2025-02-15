import pandas as pd
import numpy as np
import re
from langchain.schema import HumanMessage, SystemMessage
from langchain_community.chat_models.gigachat import GigaChat
import requests

# Авторизация в сервисе GigaChat
chat = GigaChat(credentials='OTk2OGJiNmUtMTBkYS00NmIxLTk1OTQtYzdiYTMyYmE0YjNhOjVmMDgwYTJlLWIwYmMtNGY5NC1iMmFjLTZhN2NhZjFkNDFhMw==', verify_ssl_certs=False)

messages = [
    SystemMessage(
        content="Ты лучший аналитик в компании РЖД, необходмо проанализировать данные респондента и вывести вероятность того, уйдет ли респондент от компании и перестанет пользоваться их услугами. Ты даёшь свой ответ только в виде % ухода пользователя и обоснование поставленного процента"
    )
]


# Вводим ID Получаем  -> list ["ID", "%", "Вывод", "Рекомендации"]

class ML_AGEENT:
    def __init__(self) -> None:
        self.dataframe_interesting = pd.read_excel("Интересы.xls")
        self.dataframe_waitings = pd.read_excel("Обращения.xls")
        self.dataframe_transporting = pd.read_excel("Сортированный_Объем Перевозок.xlsx")
        self.dataframe_Vladimyr = pd.read_excel("МС_Владимирская область.xls")
        self.dataframe_Kirov = pd.read_excel("МС_Кировская область.xls")
        self.dataframe_NNov = pd.read_excel("МС_Нижегородская область.xls")
        self.dataframe_MaryEl = pd.read_excel("МС_Республика Марий Эл.xls")
        self.dataframe_Mordoviya = pd.read_excel("МС_Республика Мордовия.xls")
        self.dataframe_Tatarstan = pd.read_excel("МС_Республика Татарстан.xls")
        self.dataframe_Ydmurt = pd.read_excel("МС_Республика Удмуртия.xls")
        self.dataframe_Chyvash = pd.read_excel("МС_Республика Чувашия.xls")
        self.oblast_list = [
                            self.dataframe_Vladimyr, 
                            self.dataframe_Kirov, 
                            self.dataframe_NNov, 
                            self.dataframe_MaryEl, 
                            self.dataframe_Mordoviya, 
                            self.dataframe_Tatarstan,
                            self.dataframe_Ydmurt,  
                            self.dataframe_Chyvash
                            ]


    def research(self, id:str) -> list:
        
        _, personal_data = self.research_oblasts(id)
        _, personal_seasons = self.seasons(id)
        _, personal_dop_info, sum = self.research_directions(id)
        persnal_problems = self.research_obrash(id)
        persnal_inters = self.research_interesting(id)
        
        print(sum)
        
        
        prompt = f"""У нас есть информация о клиенте железнодорожной компании и ключевое значение для анализа:


Данные о клиенте:

  Информация о юридическом лице клиента, платежеспособности и рисках: {personal_data}
  Данные о грузоперевозках клиента за последние два года: {personal_seasons}
  Информация о взаимодействиях клиента с компанией, таких как обращения за консультированием, поддержка, жалобы, благодарности и т.д.: {persnal_inters}
  Данные о проблемах клиента, возникших ранее: {persnal_problems}

Ответ формируйте строго по следующему шаблону:

Вероятность ухода: <оценка вероятности ухода в процентах>
Обоснование: <обоснование выставленной вероятности и анализ, обоснованные на данных, рекомендации по удержанию>


Пожалуйста, используйте этот формат для ответа, чтобы он мог быть автоматически распознан системой. Также, на основе полученных данных, если {sum} > 0, оцените вероятность ухода клиента и предоставьте ИНДИВИДУАЛЬНЫЕ РЕКОМЕНДАЦИИ ДЛЯ УДЕРЖАНИЯ КЛИЕНТА, если вероятность ухода составляет более 45%. Если {sum} == 0, предложите действия для возвращения клиента с высокой вероятностью ухода (100%)

САМО ОБОСНОВАНИЕ ПРОСТАВЛЕННОЙ ВЕРОЯТНОСТИ ДОЛЖНО БЫТЬ КОНСТРУКТИВНЫМ И ЛОГИЧНЫМ
"""
        
        req=requests.get('http://127.0.0.1:5500',{'text': prompt})

            
        pattern = r"Вероятность ухода:\s*(\d+%)\nОбоснование:\s*(.*)"
        
        match = re.search(pattern, req.text, re.DOTALL)

        if match:
                # Извлечение данных из групп регулярного выражения
                churn_probability = match.group(1)  # Вероятность ухода
                justification = match.group(2)  # Обоснование
                
                # Формируем структурированный ответ
                structured_data_server = {
                    "churn_probability": churn_probability,
                    "justification_server": justification
                }
                
                print(structured_data_server)
                
                return structured_data_server
            
        else:
            
            print(req.text)
        
        # messages.append(HumanMessage(content=prompt))
        # res = chat(messages)
        # messages.append(res)
            
    
    
    def research_oblasts(self, id:str) -> str:
        for i in self.oblast_list:
            filtred = i[i["ID"] == id][["ID",
                                        "Размер компании.Наименование", 
                                        "Карточка клиента (внешний источник).Индекс платежной дисциплины Описание", 
                                        "Карточка клиента (внешний источник).Индекс финансового риска Описание", 
                                        "Госконтракты.Тип контракта"]]
            if len(filtred.values.tolist()) >=1:
                break
            else:
                pass
        
        all_data = filtred.values.T.tolist()
        # print(all_data[0], all_data[1])
        all_data = [list(set(sublist)) for sublist in all_data]
        # print(all_data[0], all_data[1])
        
        final = "Этот клиент - " +   str(all_data[1]) + " C " + str(all_data[2]) + " С индексом финального риска: " + str(all_data[3]) + " И в гос контрактах он является: " + str(all_data[4])
        # print(final)
        
        return filtred, final
    
    def seasons(self, id:str) ->  str:
        
        filtred = self.dataframe_transporting[self.dataframe_transporting["ID"] == id]
        years = filtred.columns.values.tolist()[5:]
        month = filtred[years].values.T.tolist()
        month_normal = years[0::2]
        month_in_numbers =  [[sum(subarray)] for subarray in month]
        month_in_tons = month_in_numbers[1::2]
        month_in_money = month_in_numbers[0::2]
        text = ""
        for i in range(len(month_normal)):
            text += f"Клиент в год, месяц - {month_normal[i]} перевёз {month_in_tons[i]} тон груза  на сумму: {month_in_money[i]}\n"
            
        # print(text)
        
        return filtred, text

    def research_directions(self, id:str):
        
        filtred=self.dataframe_transporting[self.dataframe_transporting['ID']==id]
        all_data = filtred.values.T.tolist()
        
        text=""
        sum=0
        
        for i in range(len(all_data[3])):

            text+="| Этот клиент везет из - " + all_data[1][i] + " в - " + all_data[2][i] + "| Код товара - " + str(all_data[3][i])+"| Категория груза - "+all_data[4][i]+"|\n"
            
        # print (text)
        
        
        years = filtred.columns.values.tolist()[5:]
        month = filtred[years].values.T.tolist()
        
        
        for i in month[-8::2]:
            
            for j in i:
                
                sum+=j
                
        
        
        print(years,month)
        
        
        return all_data, text,sum

    def research_interesting(self, id:str) -> str:
        filtred = self.dataframe_interesting[self.dataframe_interesting["ID"] == id][["Состояние", "Канал первичного интереса"]]

        all_data = filtred.values.T.tolist()
        all_data = [list(set(sublist)) for sublist in all_data]

        string = ""
        ls = []

        for i in filtred.values:
            string += str(i[0]) + " " + str(i[1]) + ", "

        for i in all_data[0]:
            for j in all_data[1]:
                if string.count(f"{i} {j}") != 0:
                    ls.append([str(i) + " " + str(j), string.count(f"{i} {j}")])

        for i in ls:
            string += i[0] + " " + str(i[1]) + "\n"

        return string
    

    def research_obrash(self, id:str) -> str:
        filtred = self.dataframe_waitings[self.dataframe_waitings["ID"] == id][["Тема вопроса"]]

        all_data = filtred.values.T.tolist()
        try:
            
            string = ""
            for i in all_data:
                string += i[0] + "\n"

            print(string)
        except:
            string = "Обращений не обнаружено"
        
        return string
 
class ML_AGEENT2:
    def __init__(self) -> None:
        self.dataframe_interesting = pd.read_excel("Интересы.xls")
        self.dataframe_waitings = pd.read_excel("Обращения.xls")
        self.dataframe_transporting = pd.read_excel("Сортированный_Объем Перевозок.xlsx")
        self.dataframe_Vladimyr = pd.read_excel("МС_Владимирская область.xls")
        self.dataframe_Kirov = pd.read_excel("МС_Кировская область.xls")
        self.dataframe_NNov = pd.read_excel("МС_Нижегородская область.xls")
        self.dataframe_MaryEl = pd.read_excel("МС_Республика Марий Эл.xls")
        self.dataframe_Mordoviya = pd.read_excel("МС_Республика Мордовия.xls")
        self.dataframe_Tatarstan = pd.read_excel("МС_Республика Татарстан.xls")
        self.dataframe_Ydmurt = pd.read_excel("МС_Республика Удмуртия.xls")
        self.dataframe_Chyvash = pd.read_excel("МС_Республика Чувашия.xls")
        self.oblast_list = [
                            self.dataframe_Vladimyr, 
                            self.dataframe_Kirov, 
                            self.dataframe_NNov, 
                            self.dataframe_MaryEl, 
                            self.dataframe_Mordoviya, 
                            self.dataframe_Tatarstan,
                            self.dataframe_Ydmurt,
                            self.dataframe_Chyvash
                            ]


    def research(self, id:str) -> list:
        
        _, personal_data = self.research_oblasts(id)
        _, personal_seasons = self.seasons(id)
        _, personal_dop_info, sum = self.research_directions(id)
        persnal_problems = self.research_obrash(id)
        persnal_inters = self.research_interesting(id)
        
        
        
        
        prompt = f"""У нас есть информация о клиенте железнодорожной компании и ключевое значение для анализа:


Данные о клиенте:

  Информация о юридическом лице клиента, платежеспособности и рисках: {personal_data}
  Данные о грузоперевозках клиента за последние два года: {personal_seasons}
  Информация о взаимодействиях клиента с компанией, таких как обращения за консультированием, поддержка, жалобы, благодарности и т.д.: {persnal_inters}
  Данные о проблемах клиента, возникших ранее: {persnal_problems}

Ответ формируйте строго по следующему шаблону:

Вероятность ухода: <оценка вероятности ухода в процентах>
Обоснование: <обоснование выставленной вероятности и анализ, обоснованные на данных, рекомендации по удержанию>


Пожалуйста, используйте этот формат для ответа, чтобы он мог быть автоматически распознан системой. Также, на основе полученных данных, если {sum} > 0, оцените вероятность ухода клиента и предоставьте ИНДИВИДУАЛЬНЫЕ РЕКОМЕНДАЦИИ ДЛЯ УДЕРЖАНИЯ КЛИЕНТА, если вероятность ухода составляет более 45%. Если {sum} == 0, предложите действия для возвращения клиента с высокой вероятностью ухода (100%)

САМО ОБОСНОВАНИЕ ПРОСТАВЛЕННОЙ ВЕРОЯТНОСТИ ДОЛЖНО БЫТЬ КОНСТРУКТИВНЫМ И ЛОГИЧНЫМ
"""
        
        req=requests.get('http://127.0.0.1:5500',{'text': prompt})

            
        pattern = r"Вероятность ухода:\s*(\d+%)\nОбоснование:\s*(.*)"
        
        match = re.search(pattern, req.text, re.DOTALL)

        if match:
                # Извлечение данных из групп регулярного выражения
                churn_probability = match.group(1)  # Вероятность ухода
                justification = match.group(2)  # Обоснование
                
                # Формируем структурированный ответ
                structured_data_server = {
                    "churn_probability": churn_probability,
                    "justification_server": justification
                }
                
                print(structured_data_server)
                
                return structured_data_server
            
        else:
            
            print(req.text)
        
        # messages.append(HumanMessage(content=prompt))
        # res = chat(messages)
        # messages.append(res)
            
    
    
    def research_oblasts(self, id:str) -> str:
        for i in self.oblast_list:
            filtred = i[i["ID"] == id][["ID",
                                        "Размер компании.Наименование", 
                                        "Карточка клиента (внешний источник).Индекс платежной дисциплины Описание", 
                                        "Карточка клиента (внешний источник).Индекс финансового риска Описание", 
                                        "Госконтракты.Тип контракта"]]
            if len(filtred.values.tolist()) >=1:
                break
            else:
                pass
        
        all_data = filtred.values.T.tolist()
        # print(all_data[0], all_data[1])
        all_data = [list(set(sublist)) for sublist in all_data]
        # print(all_data[0], all_data[1])
        
        final = "Этот клиент - " +   str(all_data[1]) + " C " + str(all_data[2]) + " С индексом финального риска: " + str(all_data[3]) + " И в гос контрактах он является: " + str(all_data[4])
        # print(final)
        
        return filtred, final
    
    def seasons(self, id:str) ->  str:
        
        filtred = self.dataframe_transporting[self.dataframe_transporting["ID"] == id]
        years = filtred.columns.values.tolist()[5:]
        month = filtred[years].values.T.tolist()
        month_normal = years[0::2]
        month_in_numbers =  [[sum(subarray)] for subarray in month]
        month_in_tons = month_in_numbers[1::2]
        month_in_money = month_in_numbers[0::2]
        text = ""
        for i in range(len(month_normal)):
            text += f"Клиент в год, месяц - {month_normal[i]} перевёз {month_in_tons[i]} тон груза  на сумму: {month_in_money[i]}\n"
            
        print(text)
        
        return filtred, text

    def research_directions(self, id:str):
        
        filtred=self.dataframe_transporting[self.dataframe_transporting['ID']==id]
        all_data = filtred.values.T.tolist()
        
        text=""
        sum=0
        
        for i in range(len(all_data[3])):

            text+="| Этот клиент везет из - " + all_data[1][i] + " в - " + all_data[2][i] + "| Код товара - " + str(all_data[3][i])+"| Категория груза - "+all_data[4][i]+"|\n"
            
        # print (text)
        
        
        years = filtred.columns.values.tolist()[5:]
        month = filtred[years].values.T.tolist()
        
        
        for i in month[-8::2]:
            
            for j in i:
                
                sum+=j
                
        
        
        print(years,month)
        
        
        return all_data, text,sum

    def research_interesting(self, id:str) -> str:
        filtred = self.dataframe_interesting[self.dataframe_interesting["ID"] == id][["Состояние", "Канал первичного интереса"]]

        all_data = filtred.values.T.tolist()
        all_data = [list(set(sublist)) for sublist in all_data]

        string = ""
        ls = []

        for i in filtred.values:
            string += str(i[0]) + " " + str(i[1]) + ", "

        for i in all_data[0]:
            for j in all_data[1]:
                if string.count(f"{i} {j}") != 0:
                    ls.append([str(i) + " " + str(j), string.count(f"{i} {j}")])

        for i in ls:
            string += i[0] + " " + str(i[1]) + "\n"

        return string
    

    def research_obrash(self, id:str) -> str:
        filtred = self.dataframe_waitings[self.dataframe_waitings["ID"] == id][["Тема вопроса"]]

        all_data = filtred.values.T.tolist()
        try:
            
            string = ""
            for i in all_data:
                string += i[0] + "\n"

            print(string)
        except:
            string = "Обращений не обнаружено"
        
        return string