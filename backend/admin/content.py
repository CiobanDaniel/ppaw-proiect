"""Rute MVC pentru cărți, categorii și capitole."""

from typing import Optional

from fastapi import APIRouter, Depends, Form, Request

from .common import (
    AdminValidationError, VALID_BOOK_STATES, get_books_accessor, get_categories_accessor,
    get_chapters_accessor, get_or_404, redirect_with_feedback, require_choice,
    require_non_negative, require_present, templates,
)


router = APIRouter()


@router.get('/carti')
def books_index(request: Request, accessor=Depends(get_books_accessor)):
    return templates.TemplateResponse(request, 'admin/books/index.html', {'carti': accessor.get_all_carti()})


@router.get('/carti/creare')
def books_create_get(request: Request, accessor=Depends(get_books_accessor)):
    return templates.TemplateResponse(request, 'admin/books/create.html', {'autori': accessor.get_autori_pentru_dropdown()})


@router.post('/carti/creare')
def books_create_post(
    titlu: str = Form(...), id_autor: int = Form(...), descriere: str = Form(''),
    stare: str = Form('publicat'), accessor=Depends(get_books_accessor),
):
    accessor.add_carte(require_present(titlu, 'Titlul'), id_autor, descriere, require_choice(stare, VALID_BOOK_STATES, 'stare'))
    return redirect_with_feedback('/carti', 'success', 'Cartea a fost creată.')


@router.get('/carti/detalii/{carte_id}')
def books_details(request: Request, carte_id: int, accessor=Depends(get_books_accessor)):
    carte = get_or_404(accessor.get_carte_by_id(carte_id), 'Cartea')
    return templates.TemplateResponse(request, 'admin/books/details.html', {'carte': carte})


@router.get('/carti/editare/{carte_id}')
def books_edit_get(request: Request, carte_id: int, accessor=Depends(get_books_accessor)):
    carte = get_or_404(accessor.get_carte_by_id(carte_id), 'Cartea')
    return templates.TemplateResponse(request, 'admin/books/edit.html', {'carte': carte, 'autori': accessor.get_autori_pentru_dropdown()})


@router.post('/carti/editare/{carte_id}')
def books_edit_post(
    carte_id: int, titlu: str = Form(...), id_autor: int = Form(...), descriere: str = Form(''),
    stare: str = Form('publicat'), accessor=Depends(get_books_accessor),
):
    get_or_404(accessor.update_carte(carte_id, require_present(titlu, 'Titlul'), id_autor, descriere, require_choice(stare, VALID_BOOK_STATES, 'stare')), 'Cartea')
    return redirect_with_feedback('/carti', 'success', 'Cartea a fost actualizată.')


@router.get('/categorii')
def categories_index(request: Request, accessor=Depends(get_categories_accessor)):
    return templates.TemplateResponse(request, 'admin/categories/index.html', {'categorii': accessor.get_toate_categoriile()})


@router.get('/categorii/creare')
def categories_create_get(request: Request):
    return templates.TemplateResponse(request, 'admin/categories/create.html', {})


@router.post('/categorii/creare')
def categories_create_post(nume: str = Form(...), descriere: Optional[str] = Form(None), accessor=Depends(get_categories_accessor)):
    accessor.add_categorie(require_present(nume, 'Numele categoriei'), descriere)
    return redirect_with_feedback('/categorii', 'success', 'Categoria a fost creată.')


@router.get('/categorii/editare/{cat_id}')
def categories_edit_get(request: Request, cat_id: int, accessor=Depends(get_categories_accessor)):
    categorie = get_or_404(accessor.get_categorie_by_id(cat_id), 'Categoria')
    return templates.TemplateResponse(request, 'admin/categories/edit.html', {'categorie': categorie})


@router.post('/categorii/editare/{cat_id}')
def categories_edit_post(cat_id: int, nume: str = Form(...), descriere: Optional[str] = Form(None), accessor=Depends(get_categories_accessor)):
    get_or_404(accessor.update_categorie(cat_id, require_present(nume, 'Numele categoriei'), descriere), 'Categoria')
    return redirect_with_feedback('/categorii', 'success', 'Categoria a fost actualizată.')


def validate_chapter(numar_capitol: int, cost_puncte: int, stare: str, este_gratuit: Optional[str]) -> bool:
    if numar_capitol < 1:
        raise AdminValidationError('Numărul capitolului trebuie să fie cel puțin 1.')
    require_non_negative(cost_puncte, 'Costul în puncte')
    require_choice(stare, VALID_BOOK_STATES, 'stare')
    is_free = este_gratuit == 'on'
    if not is_free and cost_puncte == 0:
        raise AdminValidationError('Un capitol plătit trebuie să aibă un cost mai mare decât zero.')
    return is_free


@router.get('/capitole')
def chapters_index(request: Request, accessor=Depends(get_chapters_accessor)):
    return templates.TemplateResponse(request, 'admin/chapters/index.html', {'capitole': accessor.get_toate_capitolele()})


@router.get('/capitole/detalii/{cap_id}')
def chapters_details(request: Request, cap_id: int, accessor=Depends(get_chapters_accessor)):
    capitol = get_or_404(accessor.get_capitol_by_id(cap_id), 'Capitolul')
    return templates.TemplateResponse(request, 'admin/chapters/details.html', {'capitol': capitol})


@router.get('/capitole/creare')
def chapters_create_get(request: Request, accessor=Depends(get_chapters_accessor)):
    return templates.TemplateResponse(request, 'admin/chapters/create.html', {'carti': accessor.get_carti_pentru_dropdown()})


@router.post('/capitole/creare')
def chapters_create_post(
    id_carte: int = Form(...), numar_capitol: int = Form(...), titlu: str = Form(...), continut: str = Form(...),
    cost_puncte: int = Form(0), stare: str = Form('ciorna'), este_gratuit: Optional[str] = Form(None),
    accessor=Depends(get_chapters_accessor),
):
    is_free = validate_chapter(numar_capitol, cost_puncte, stare, este_gratuit)
    accessor.add_capitol(id_carte, numar_capitol, require_present(titlu, 'Titlul'), require_present(continut, 'Conținutul'), is_free, cost_puncte, stare)
    return redirect_with_feedback('/capitole', 'success', 'Capitolul a fost creat.')


@router.get('/capitole/editare/{cap_id}')
def chapters_edit_get(request: Request, cap_id: int, accessor=Depends(get_chapters_accessor)):
    capitol = get_or_404(accessor.get_capitol_by_id(cap_id), 'Capitolul')
    return templates.TemplateResponse(request, 'admin/chapters/edit.html', {'capitol': capitol, 'carti': accessor.get_carti_pentru_dropdown()})


@router.post('/capitole/editare/{cap_id}')
def chapters_edit_post(
    cap_id: int, id_carte: int = Form(...), numar_capitol: int = Form(...), titlu: str = Form(...), continut: str = Form(...),
    cost_puncte: int = Form(0), stare: str = Form('ciorna'), este_gratuit: Optional[str] = Form(None),
    accessor=Depends(get_chapters_accessor),
):
    is_free = validate_chapter(numar_capitol, cost_puncte, stare, este_gratuit)
    get_or_404(accessor.update_capitol(cap_id, id_carte, numar_capitol, require_present(titlu, 'Titlul'), require_present(continut, 'Conținutul'), is_free, cost_puncte, stare), 'Capitolul')
    return redirect_with_feedback('/capitole', 'success', 'Capitolul a fost actualizat.')
