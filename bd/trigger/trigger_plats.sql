DELIMITER |
create or replace trigger trg_update_stock_plats after insert on APPARTENIR_PLATS for each row
begin
    if (select stock from PLATS where id_plat = new.id_plat)- new.quantite >= 0 then
        update PLATS set stock = stock - new.quantite where id_plat = new.id_plat;
    else
        signal sqlstate '45000' set message_text = 'Stock insuffisant pour le plat avec id_plat = ' || new.id_plat;
    end if;
end |
DELIMITER ;

DELIMITER |
create or replace trigger trg_update_stock_menus before insert on APPARTENIR_MENUS for each row
begin
    declare fini BOOLEAN default false;
    declare plat_id INT;
    declare les_plats cursor for 
        select id_plat from CONTENIR where id_menu = new.id_menu;

    declare continue handler for not found set fini = true;

    open les_plats;
    while not fini do
        fetch les_plats into plat_id;
        if not fini then
            if (select stock from PLATS where id_plat = plat_id) - new.quantite < 0 then
                signal sqlstate '45000' set message_text = 'Stock insuffisant pour le plat avec id_plat = ' || plat_id || ' dans le menu avec id_menu = ' || new.id_menu;
            end if;
            update PLATS set stock = stock - new.quantite where id_plat = plat_id;¡
        end if;
    end while;
    close les_plats;
end |