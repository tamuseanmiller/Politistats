# form learned from https://www.youtube.com/watch?v=3XOS_UpJirU

# Django choice fields learned from https://www.geeksforgeeks.org/choicefield-django-forms/  ,  https://www.kite.com/python/examples/5577/django-add-a-%60choicefield%60-to-a-form-
# List of states was taken from https://en.wikipedia.org/wiki/List_of_states_and_territories_of_the_United_States

from django import forms


class StateForm(forms.Form):
    # state = forms.CharField(label='')
    # dropDownSelection = forms.ChoiceField(choices=[("AL","AL"), ("AK","AK"), ("AZ","AZ"), ("AR","AR"), ("CA","CA"), ("CO","CO"), ("CT","CT"), ("DE","DE")])
    state = forms.ChoiceField(label='',
                              choices=[("", "STATE"), ("AL", "Alabama"), ("AK", "Alaska"), ("AZ", "Arizona"),
                                       ("AR", "Arkansas"), ("CA", "California"), ("CO", "Colorado"),
                                       ("CT", "Connecticut"), ("DE", "Delaware"), ("DC", "Washington DC"),
                                       ("FL", "Florida"), ("GA", "Georgia"), ("HI", "Hawaii"), ("ID", "Idaho"),
                                       ("IL", "Illinois"), ("IN", "Indiana"), ("IA", "Iowa"), ("KS", "Kansas"),
                                       ("KY", "Kentucky"), ("LA", "Los Angeles"), ("ME", "Maine"), ("MD", "Maryland"),
                                       ("MA", "Massachusetts"), ("MI", "Michigan"), ("MN", "Minnesota"),
                                       ("MS", "Mississippi"), ("MO", "Missouri"), ("MT", "Montana"), ("NE", "Nebraska"),
                                       ("NV", "Nevada"), ("NH", "New Hampshire"), ("NJ", "New Jersey"),
                                       ("NM", "New Mexico"), ("NY", "New York"), ("NC", "North Carolina"),
                                       ("ND", "North Dakota"), ("OH", "Ohio"), ("OK", "Oklahoma"), ("OR", "Oregon"),
                                       ("PA", "Pennsylvania"), ("RI", "Rhode Island"), ("SC", "South Carolina"),
                                       ("SD", "South Dakota"), ("TN", "Tennessee"), ("TX", "Texas"), ("UT", "Utah"),
                                       ("VT", "Vermont"), ("VA", "Virginia"), ("WA", "Washington"),
                                       ("WV", "West Virginia"), ("WI", "Wisconsin"), ("WY", "Wyoming")])


# Hidden fields learned from https://stackoverflow.com/questions/18417274/django-form-without-any-fields
class PersonForm(forms.Form):
    state = forms.CharField(widget=forms.HiddenInput())
