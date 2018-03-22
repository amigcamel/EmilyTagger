# -*-coding:utf-8-*-
from django import forms


FILE_SIZE_LIMIT = 5000  # KB


class UploadTextForm(forms.Form):
    upload_file = forms.FileField(
        required=False,
        label=("請選擇文本(可複選)"),
        help_text="檔案大小限制: %d KB" %
        FILE_SIZE_LIMIT,
        widget=forms.FileInput(
            attrs={
                'multiple': 'multiple'}))
    title = forms.CharField(
        required=False,
        label=('標題'),
        widget=forms.TextInput(
            attrs={
                'class': 'form-control'}))
    source = forms.CharField(
        required=False,
        label=('來源'),
        widget=forms.TextInput(
            attrs={
                'class': 'form-control'}))
    category = forms.CharField(
        required=False,
        label=('分類'),
        widget=forms.TextInput(
            attrs={
                'class': 'form-control'}))

    def clean_upload_file(self):
        file_size_limit = FILE_SIZE_LIMIT * 1024
        upload_file = self.cleaned_data['upload_file']
        if upload_file is None:
            return upload_file
        if upload_file.content_type != 'text/plain':
            raise forms.ValidationError('You have to upload a text file')

        if upload_file.size > file_size_limit:
            raise forms.ValidationError(
                (
                    'Please keep the file size under %d KB. '
                    ' Current size is %.1f KB.'
                ) %
                (FILE_SIZE_LIMIT, upload_file.size / 1000.0))
        box = ''
        for chunk in upload_file.chunks():
            box += chunk
        try:
            box.decode('utf-8')
        except BaseException:
            raise forms.ValidationError('File should be encoded in utf-8')
        return box


class PasteTextForm(forms.Form):
    post = forms.CharField(required=False, label=(''), widget=forms.Textarea(
        attrs={'class': 'form-control', 'rows': 20, 'required': 'required'}))
    title = forms.CharField(
        required=False,
        label=('標題'),
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'required': 'required'}))
    source = forms.CharField(
        required=False,
        label=('來源'),
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'required': 'required'}))
    category = forms.CharField(
        required=False,
        label=('分類'),
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'required': 'required'}))


class ModifyTagForm(forms.Form):
    tag_schema = forms.CharField(
        required=False,
        label=(''),
        widget=forms.Textarea(
            attrs={
                'class': 'form-control',
                'rows': 20}))
