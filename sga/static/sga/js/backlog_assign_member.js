const assignable_members = JSON.parse(
  document.getElementById("assignable_members").textContent
);

const us_estimation = Number(
  document.getElementById("us_estimation").textContent
);

const member_id_select = document.getElementById("id_sprint_member");
const original_member_id = member_id_select.value;
updateMemberInfo(original_member_id);

member_id_select.addEventListener("change", function() {
  const memberId = this.value;
  updateMemberInfo(memberId);
});

function updateMemberInfo(memberId){
  const member = assignable_members.find(m => m.id == memberId);
  const divMemberInfo = document.getElementById("member-info");
  if (!member) {
    divMemberInfo.innerHTML = `<p>Estimación de la US: ${us_estimation} Hs</p>`;
    return;
  }
  let {capacity, used_capacity} = member;
  if(original_member_id !== memberId){
    used_capacity += us_estimation;
  }
  const remaining_capacity = capacity - used_capacity;

  divMemberInfo.innerHTML = `
  <p>Estimación de la US: ${us_estimation} Hs</p>
  <p>Capacidad del miembro: ${capacity} Hs</p>
  <p>Capacidad asignada al miembro luego de asignar la US: ${used_capacity} Hs</p>
  <p>Capacidad del miembro restante en el sprint: ${remaining_capacity} Hs</p>`;
}