from django.shortcuts import render, get_object_or_404
from .models import Post
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .forms import EmailPostForm
from django.core.mail import send_mail


def post_list(request):
    post_list = Post.published.all()
    # paginacion con 3 publicaciones por pagina
    paginator = Paginator(post_list, 3)
    page_number = request.GET.get("page", 1)
    try:
        posts = paginator.page(page_number)
    except PageNotAnInteger:
        # si el page_number no es un numero, va a la primera pagina
        posts = paginator.page(1)
    except EmptyPage:
        # si en numero de pagina esta fuera de rango obtiene la ultima pagina
        posts = paginator.page(paginator.num_pages)

    return render(request, "blog/post/list.html", {"posts": posts})


def post_detail(request, year, month, day, post):
    post = get_object_or_404(
        Post,
        slug=post,
        publish__year=year,
        publish__month=month,
        publish__day=day,
        status=Post.Status.PUBLISHED,
    )
    return render(request, "blog/post/detail.html", {"post": post})


def post_share(request, post_id):
    # recibe un id
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)

    sent = False

    if request.method == "POST":
        # los campos del formulario que pasaron la validacion
        form = EmailPostForm(request.POST)
        if form.is_valid():
            # el formulario pasa la validacion
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = (
                f"{cd['name']} ({cd['email']}) " f"recommends you read {post.title}"
            )
            message = (
                f"Lee el post de mi blog: {post.title} \nHaz clic asi: {post_url}\n\n"
                f"Te lo envia tu amigo: {cd['name']}, con el siguiente mensaje: {cd['comments']}"
            )
            send_mail(
                subject=subject,
                message=message,
                from_email=None,
                recipient_list=[cd["to"]],
            )
            sent = True
    else:
        form = EmailPostForm()
    return render(
        request, "blog/post/share.html", {"post": post, "form": form, "sent": sent}
    )
