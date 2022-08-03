from django import template


register = template.Library()

@register.simple_tag(name="get_webcam_address", takes_context=True)
def get_webcam_address(context):
	request = context['request']
	return ' '.join([str(elem) for elem in request.get_host().split(':')[0:1]]) + ':90'