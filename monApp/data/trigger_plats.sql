create or replace trigger trg_update_stock_plats after insert on APPARTENIR_PLATS for each row
begin
    if (select stock from PLATS where id_plat = new.id_plat)- new.quantite >= 0 then
        update PLATS set stock = stock - new.quantite where id_plat = new.id_plat;
    else
        signal sqlstate '45000' set message_text = 'Stock insuffisant pour le plat avec id_plat = ' || new.id_plat;
    end if;
end ;