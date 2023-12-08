from django import forms

class ForecastForm(forms.Form):
    symbol_dropdown = forms.ChoiceField(choices=(),required=True)
    column_dropdown = forms.ChoiceField(choices=(),required=True)
    frequency_dropdown = forms.ChoiceField(choices=(),required=True)


    def __init__(self,*args,**kwargs):
        symbols = kwargs.pop('symbols',[])
        columns = kwargs.pop('columns',[])
        frequency = kwargs.pop('frequency',[])


        super().__init__(*args,**kwargs)

        #update choices for the symbol and column dropdown field 
        self.fields['symbol_dropdown'].choices = [(symbol,symbol) for symbol in symbols]
        self.fields['column_dropdown'].choices = [(column,column) for column in columns]
        self.fields['frequency_dropdown'].choices = [(freq,freq) for freq in frequency]
