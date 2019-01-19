from django.shortcuts import render

# Create your views here.

from .models import Book, Author, BookInstance, Genre, Game, CustomUser
from django.urls import reverse_lazy
from django.views import generic

from .forms import CustomUserCreationForm

class SignUp(generic.CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'signup.html'


def profile(request):
        if request.method == "POST":
            return render(request, "users/profile.html")
        else:
            return render(request, "users/profile.html")


def index(request):
    """
    View function for home page of site.
    """
    # Generate counts of some of the main objects
    num_books=Book.objects.all().count()
    num_instances=BookInstance.objects.all().count()
    # Available copies of books
    num_instances_available=BookInstance.objects.filter(status__exact='a').count()
    num_authors=Author.objects.count()  # The 'all()' is implied by default.

    # Number of visits to this view, as counted in the session variable.
    num_visits=request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits+1
    
    # Render the HTML template index.html with the data in the context variable.
    return render(
        request,
        'index.html',
        context={'num_books':num_books,'num_instances':num_instances,'num_instances_available':num_instances_available,'num_authors':num_authors,
            'num_visits':num_visits},
    )

from django.views import generic



class GameListView(generic.ListView):
    """
    Generic class-based view for a list of games.
    """
    model = Game
    paginate_by = 10

class GameDetailView(generic.DetailView):
    """
    Generic class-based detail view for a game.
    """
    model = Game


class BookListView(generic.ListView):
    """
    Generic class-based view for a list of books.
    """
    model = Book
    paginate_by = 10
    
class BookDetailView(generic.DetailView):
    """
    Generic class-based detail view for a book.
    """
    model = Book

class AuthorListView(generic.ListView):
    """
    Generic class-based list view for a list of authors.
    """
    model = Author
    paginate_by = 10 


class AuthorDetailView(generic.DetailView):
    """
    Generic class-based detail view for an author.
    """
    model = Author

class PlayerDetailView(generic.DetailView):

    
    model = CustomUser


from django.contrib.auth.mixins import LoginRequiredMixin

class LoanedBooksByUserListView(LoginRequiredMixin,generic.ListView):
    """
    Generic class-based view listing books on loan to current user. 
    """
    model = BookInstance
    template_name ='users/bookinstance_list_borrowed_user.html'
    paginate_by = 10
    
    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')


# Added as part of challenge!
from django.contrib.auth.mixins import PermissionRequiredMixin

class LoanedBooksAllListView(PermissionRequiredMixin,generic.ListView):
    """
    Generic class-based view listing all books on loan. Only visible to users with can_mark_returned permission.
    """
    model = BookInstance
    permission_required = 'users.can_mark_returned'
    template_name ='users/bookinstance_list_borrowed_all.html'
    paginate_by = 10
    
    def get_queryset(self):
        return BookInstance.objects.filter(status__exact='o').order_by('due_back')  


from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
import datetime
from django.contrib.auth.decorators import permission_required

from .forms import RenewBookForm

@permission_required('users.can_mark_returned')
def renew_book_librarian(request, pk):
    """
    View function for renewing a specific BookInstance by librarian
    """
    book_inst=get_object_or_404(BookInstance, pk = pk)

    # If this is a POST request then process the Form data
    if request.method == 'POST':

        # Create a form instance and populate it with data from the request (binding):
        form = RenewBookForm(request.POST)

        # Check if the form is valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            book_inst.due_back = form.cleaned_data['renewal_date']
            book_inst.save()

            # redirect to a new URL:
            return HttpResponseRedirect(reverse('all-borrowed') )

    # If this is a GET (or any other method) create the default form
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={'renewal_date': proposed_renewal_date,})

    return render(request, 'users/book_renew_librarian.html', {'form': form, 'bookinst':book_inst})
    
    
    
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Author


class AuthorCreate(PermissionRequiredMixin, CreateView):
    model = Author
    fields = '__all__'
    initial={'date_of_death':'05/01/2018',}
    permission_required = 'users.can_mark_returned'

class AuthorUpdate(PermissionRequiredMixin, UpdateView):
    model = Author
    fields = ['first_name','last_name','date_of_birth','date_of_death']
    permission_required = 'users.can_mark_returned'

class AuthorDelete(PermissionRequiredMixin, DeleteView):
    model = Author
    success_url = reverse_lazy('authors')
    permission_required = 'users.can_mark_returned'
    

#Classes created for the forms challenge
class BookCreate(PermissionRequiredMixin, CreateView):
    model = Book
    fields = '__all__'
    permission_required = 'users.can_mark_returned'

class BookUpdate(PermissionRequiredMixin, UpdateView):
    model = Book
    fields = '__all__'
    permission_required = 'users.can_mark_returned'

class BookDelete(PermissionRequiredMixin, DeleteView):
    model = Book
    success_url = reverse_lazy('books')
    permission_required = 'users.can_mark_returned'



class AllSearchListView(generic.ListView):
    model = Game
    paginate_by = 10

    def get_queryset(self):
        query = self.request.GET.get('q')
        if query == None:
            return Game.objects.none()
        return Game.objects.filter(name__contains=self.request.GET.get('q'))







