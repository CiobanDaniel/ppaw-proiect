"""Rute MVC pentru utilizatori, recenzii și comentarii."""

from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Form, Request

from .common import (
    AdminValidationError, VALID_ROLES, get_comments_accessor, get_or_404,
    get_reviews_accessor, get_users_accessor, redirect_with_feedback,
    require_choice, require_present, templates,
)


router = APIRouter()


@router.get('/utilizatori')
def users_index(request: Request, accessor=Depends(get_users_accessor)):
    return templates.TemplateResponse(request, 'admin/users/index.html', {'utilizatori': accessor.get_all_users()})


@router.get('/utilizatori/detalii/{user_id}')
def users_details(request: Request, user_id: int, accessor=Depends(get_users_accessor)):
    utilizator = get_or_404(accessor.get_user_by_id(user_id), 'Utilizatorul')
    return templates.TemplateResponse(request, 'admin/users/details.html', {'utilizator': utilizator})


@router.get('/utilizatori/creare')
def users_create_get(request: Request):
    return templates.TemplateResponse(request, 'admin/users/create.html', {})


@router.post('/utilizatori/creare')
def users_create_post(
    nume_utilizator: str = Form(...), email: str = Form(...), parola_hash: str = Form(...),
    rol: str = Form('cititor'), telefon: Optional[str] = Form(None), adresa: Optional[str] = Form(None),
    data_nasterii: Optional[date] = Form(None), accessor=Depends(get_users_accessor),
):
    accessor.add_entity(
        require_present(nume_utilizator, 'Numele utilizatorului'), require_present(email, 'Emailul'),
        require_present(parola_hash, 'Parola demonstrativă'), require_choice(rol, VALID_ROLES, 'rol'),
        telefon, adresa, data_nasterii,
    )
    return redirect_with_feedback('/utilizatori', 'success', 'Utilizatorul a fost creat.')


@router.get('/utilizatori/editare/{user_id}')
def users_edit_get(request: Request, user_id: int, accessor=Depends(get_users_accessor)):
    utilizator = get_or_404(accessor.get_user_by_id(user_id), 'Utilizatorul')
    return templates.TemplateResponse(request, 'admin/users/edit.html', {'utilizator': utilizator})


@router.post('/utilizatori/editare/{user_id}')
def users_edit_post(
    user_id: int, nume_utilizator: str = Form(...), email: str = Form(...), rol: str = Form('cititor'),
    telefon: Optional[str] = Form(None), adresa: Optional[str] = Form(None), data_nasterii: Optional[date] = Form(None),
    accessor=Depends(get_users_accessor),
):
    get_or_404(accessor.update_entity(
        user_id, require_present(nume_utilizator, 'Numele utilizatorului'), require_present(email, 'Emailul'),
        require_choice(rol, VALID_ROLES, 'rol'), telefon, adresa, data_nasterii,
    ), 'Utilizatorul')
    return redirect_with_feedback('/utilizatori', 'success', 'Utilizatorul a fost actualizat.')


@router.post('/utilizatori/stergere/{user_id}')
def users_delete_post(user_id: int, accessor=Depends(get_users_accessor)):
    get_or_404(accessor.soft_delete(user_id), 'Utilizatorul')
    return redirect_with_feedback('/utilizatori', 'success', 'Utilizatorul a fost șters logic.')


@router.get('/recenzii')
def reviews_index(request: Request, accessor=Depends(get_reviews_accessor)):
    return templates.TemplateResponse(request, 'admin/reviews/index.html', {'recenzii': accessor.get_toate_recenziile()})


@router.get('/recenzii/editare/{rec_id}')
def reviews_edit_get(request: Request, rec_id: int, accessor=Depends(get_reviews_accessor)):
    recenzie = get_or_404(accessor.get_recenzie_by_id(rec_id), 'Recenzia')
    return templates.TemplateResponse(request, 'admin/reviews/edit.html', {'recenzie': recenzie})


@router.post('/recenzii/editare/{rec_id}')
def reviews_edit_post(rec_id: int, nota: int = Form(...), text_comentariu: str = Form(...), accessor=Depends(get_reviews_accessor)):
    if not 1 <= nota <= 5:
        raise AdminValidationError('Nota trebuie să fie între 1 și 5.')
    get_or_404(accessor.update_recenzie(rec_id, nota, require_present(text_comentariu, 'Textul recenziei')), 'Recenzia')
    return redirect_with_feedback('/recenzii', 'success', 'Recenzia a fost actualizată.')


@router.post('/recenzii/stergere/{rec_id}')
def reviews_delete_post(rec_id: int, accessor=Depends(get_reviews_accessor)):
    get_or_404(accessor.hard_delete(rec_id), 'Recenzia')
    return redirect_with_feedback('/recenzii', 'success', 'Recenzia a fost ștearsă definitiv.')


@router.get('/comentarii')
def comments_index(request: Request, accessor=Depends(get_comments_accessor)):
    return templates.TemplateResponse(request, 'admin/comments/index.html', {'comentarii': accessor.get_toate_comentariile()})


@router.get('/comentarii/editare/{com_id}')
def comments_edit_get(request: Request, com_id: int, accessor=Depends(get_comments_accessor)):
    comentariu = get_or_404(accessor.get_comentariu_by_id(com_id), 'Comentariul')
    return templates.TemplateResponse(request, 'admin/comments/edit.html', {'comentariu': comentariu})


@router.post('/comentarii/editare/{com_id}')
def comments_edit_post(com_id: int, continut: str = Form(...), accessor=Depends(get_comments_accessor)):
    get_or_404(accessor.update_comentariu(com_id, require_present(continut, 'Conținutul comentariului')), 'Comentariul')
    return redirect_with_feedback('/comentarii', 'success', 'Comentariul a fost actualizat.')


@router.post('/comentarii/stergere/{com_id}')
def comments_delete_post(com_id: int, accessor=Depends(get_comments_accessor)):
    get_or_404(accessor.hard_delete(com_id), 'Comentariul')
    return redirect_with_feedback('/comentarii', 'success', 'Comentariul a fost șters definitiv.')
