import pandas as pd
import numpy as np
import plotly.express as px


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
        
        prompt = ""
        ...
    
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
        print(all_data[0], all_data[1])
        all_data = [list(set(sublist)) for sublist in all_data]
        print(all_data[0], all_data[1])
        
        final = "Этот клиент - " +   str(all_data[1]) + " C " + str(all_data[2]) + " С индексом финального риска: " + str(all_data[3]) + " И в гос контрактах он является: " + str(all_data[4])
        print(final)
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
    
    def research_interesting(self, id:str) -> str:
        filtred = self.dataframe_interesting[self.dataframe_interesting["ID"] == id]
    
        all_data = filtred.values.T.tolist()
        print(all_data[0], all_data[1])
        
        return filtred
    def research_waitings(self, id:str) -> str:
        filtred = self.dataframe_waitings[self.dataframe_waitings["ID"] == id]
    
        all_data = filtred.values.T.tolist()
        print(all_data[0], all_data[1])
        
        return filtred
    
    def grafic(self):




        print(vidi)


        
       

agent = ML_AGEENT()
id = 11
agent.grafic()