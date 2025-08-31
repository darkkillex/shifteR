from datetime import date,timedelta

def generate_ics(employee_name:str, items:list[dict])->str:
    lines=['BEGIN:VCALENDAR','VERSION:2.0','PRODID:-//Shift Suite//IT']
    for it in items:
        d:date=it['date']; dtend_date=d+(timedelta(days=1) if it['overnight'] else timedelta())
        lines+=['BEGIN:VEVENT',f"SUMMARY:{it['title']}",f"DTSTART:{d.strftime('%Y%m%d')}T{it['start_hhmm'].replace(':','')}00",f"DTEND:{dtend_date.strftime('%Y%m%d')}T{it['end_hhmm'].replace(':','')}00",f"DESCRIPTION:{employee_name}", 'END:VEVENT']
    lines.append('END:VCALENDAR'); return '\r\n'.join(lines)
