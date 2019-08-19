import datetime

from django import forms


class ScheduleDataForm(forms.Form):
    schedule_data = forms.CharField(widget=forms.Textarea(attrs={'placeholder': '8/19 5-10'}))
    summary = forms.CharField()
    description = forms.CharField(required=False)

    def __init__(self, *args, **kwargs):
        calendars = kwargs.pop('calendars', [])
        super().__init__(*args, **kwargs)
        calendar_choices = []
        for calendar in calendars:
            calendar_choices.append((calendar['id'], calendar['summary']))
        self.fields['calendar'] = forms.ChoiceField(choices=calendar_choices)

    def compose_datetime(self, today, parsed_date, parsed_time):
        hour_minute = parsed_time.split(':')
        hour = int(hour_minute[0])
        if hour < 12:
            hour = hour + 12
        kwargs = {'year': today.year, 'hour': hour}
        if len(hour_minute) > 1:
            kwargs['minute'] = int(hour_minute[1])
        parsed_date = parsed_date.replace(**kwargs)
        return parsed_date

    def clean_schedule_data(self):
        data = self.cleaned_data['schedule_data']
        elements = data.split()
        num_elements = len(elements)
        if num_elements % 2 != 0:
            raise forms.ValidationError("Data must be in date/time pairs")

        today = datetime.date.today()
        parsed_data = []
        for i in range(0, num_elements, 2):
            date_value = elements[i]
            time_value = elements[i+1]
            parsed_time = time_value.split('-')
            if len(parsed_time) == 2:
                parsed_date = datetime.datetime.strptime(date_value, '%m/%d')
                start_date = self.compose_datetime(today, parsed_date, parsed_time[0])
                end_date = self.compose_datetime(today, parsed_date, parsed_time[1])
                parsed_data.append((start_date, end_date))

        return parsed_data
