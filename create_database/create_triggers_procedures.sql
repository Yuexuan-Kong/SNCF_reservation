use my_sncf_reservation;

#delete old billets
delimiter //
drop procedure delete_old;
create procedure delete_old()
begin
	declare curdate date;
    set curdate=curdate();
DELETE FROM Billets
WHERE datediff(depart,curdate)<0;
alter table Billets auto_increment=1;
end; //
delimiter ;

drop trigger book_ticket;
create trigger book_ticket
after insert on Booked_tickets
for each row
begin
UPDATE Seats s
SET s.available=0
WHERE s.id_billet = NEW.id_billet and s.num_seat = NEW.num_seat and s.num_voiture = NEW.num_voiture;
update Voitures v
set v.nb_place = v.nb_place - 1
where v.id_billet = NEW.id_billet and v.num_voiture = NEW.num_voiture;
end;

drop trigger add_billet;
create trigger add_billet
after insert on Billets for each row
begin
  DECLARE i INT DEFAULT 1;
  declare m int default 1;
  declare s int default 1;
  declare nb_voitures int;
  declare nb_seats int;
  select Trains.nb_voitures into nb_voitures from Trains where Trains.id_train = NEW.id_train;
  select Trains.nb_seats into nb_seats from Trains where Trains.id_train = NEW.id_train;
  WHILE (i < nb_voitures+1) DO
  INSERT INTO Voitures (id_billet, num_voiture, nb_place) VALUES (new.id_billet, i, nb_seats);
  SET i = i + 1;
  END WHILE;
  WHILE (m < nb_voitures+1) DO
         while(s<nb_seats+1) do
          INSERT INTO Seats (id_billet, num_voiture, num_seat,fenetre_couloir) VALUES (new.id_billet, m, s,'f');
          SET s = s + 1;
          end while;
        set m = m + 1;
        set s = 1;
 END WHILE;
    update Seats set fenetre_couloir = 'c' where num_seat mod 2 = 0;
END;

delimiter //
drop procedure find_trajets;
# find possible routes on the depart date
create procedure find_trajets(in depart_date datetime)
begin
select distinct date(depart), gare_depart, gare_arrive
from Billets natural join Trajets
where date(depart)=depart_date;
end//
//
delimiter ;

# call find_trajets('2021/12/28');

delimiter //
drop procedure find_timings;
# find timings of certain routes on certain date
create procedure find_timings(in depart_date datetime, in gare_depart varchar(30), in gare_arrivee varchar(30))
begin
select time(depart), id_trajet, id_billet
from Billets natural join Trajets
where date(depart)=depart_date and Trajets.gare_depart = gare_depart and gare_arrive = gare_arrivee;
end//
//
delimiter ;

# call find_timings('2021/12/28', 'Gare de Part-Dieu', 'Gare de Saint Charles');

delimiter //
drop procedure find_voitures;
create procedure find_voitures(in billet int)
begin
select id_billet
from Voitures group by id_billet having sum(nb_place) >0 and id_billet = billet;
end//
//

delimiter ;