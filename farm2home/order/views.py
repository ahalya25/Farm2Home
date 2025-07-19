# views.py (in orders or consumer app)
from django.views.generic import TemplateView
from order.models import Orders
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404
from farmer.models import Farmer
from django.contrib.auth.decorators import login_required


class ConsumerDashboardView(TemplateView):

    template_name = 'order/consumer_dashboard.html'

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        context['orders'] = Orders.objects.filter(consumer=self.request.user).order_by('-ordered_at')

        Orders.objects.filter(consumer=self.request.user)

        return context
    

class FarmerDashboardView(TemplateView):

    template_name = 'order/farmer-dashboard.html'

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        # THE FIX: Change 'user' to 'profile' based on the FieldError
        farmer = get_object_or_404(Farmer, profile=self.request.user)

        context['orders'] = Orders.objects.filter(product__farmer=farmer).order_by('-ordered_at')

        return context
    
    
@login_required
def role_redirect_view(request):

    if hasattr(request.user, 'Consumer'):

        return redirect('consumer_dashboard')
    
    elif hasattr(request.user, 'Farmer'):

        return redirect('farmer-dashboard')
    
    return redirect('home')
