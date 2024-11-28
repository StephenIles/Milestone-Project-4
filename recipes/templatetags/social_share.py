from django import template
from django.urls import reverse
from urllib.parse import quote

register = template.Library()

@register.simple_tag(takes_context=True)
def social_share_url(context, platform, recipe):
    request = context['request']
    base_url = f"{request.scheme}://{request.get_host()}"
    recipe_url = base_url + reverse('recipes:recipe_detail', args=[recipe.pk])
    title = quote(recipe.title)
    
    urls = {
        'facebook': f"https://www.facebook.com/sharer/sharer.php?u={recipe_url}",
        'twitter': f"https://twitter.com/intent/tweet?text={title}&url={recipe_url}",
        'pinterest': f"https://pinterest.com/pin/create/button/?url={recipe_url}&media={base_url}{recipe.image.url if recipe.image else ''}&description={title}",
        'email': f"mailto:?subject={title}&body={recipe_url}"
    }
    
    return urls.get(platform, '')