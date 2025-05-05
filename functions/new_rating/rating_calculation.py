import pandas as pd
import func
import datetime

folder=rf"E:\parsed_demos\.demo\parsed"

rating_calculations=func.calculate_ratings(folder)
rating_calculations.to_excel(fr"rating_calculations_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.xlsx")
    

