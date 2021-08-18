import cv2
import os
from  preprocessing import Preprocessing
import settings

calendar = cv2.imread(os.path.join(settings.BASE_DIR, 'data', 'preprocessing', 'calendar_screenshot.jpg'))

p = Preprocessing(original_calendar=calendar)

result = p.main()
print(result)