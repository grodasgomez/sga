const user_stories = JSON.parse(
  document.getElementById("user_stories").textContent
);

const us_types = JSON.parse(document.getElementById("us_types").textContent);

const projectId = Number(document.getElementById("project_id").textContent);

const currentMember = JSON.parse(
  document.getElementById("current_member").textContent
);

let activeUsType = us_types[0];

let currentBoards = createBoard(activeUsType);

const kanban = new jKanban({
  element: "#myKanban",
  gutter: "20px",
  widthBoard: "300px",
  dragBoards: false,
  boards: currentBoards,
  dropEl: function (el, target) {
    const kanbanUsId = el.getAttribute("data-eid");
    const usId = kanbanUsId.split("-")[1];
    const us = user_stories.find((us) => us.id === parseInt(usId));

    const kanbanColumn = target.parentElement.getAttribute("data-id");
    const targetUsTypeColumn = activeUsType.columns.indexOf(
      kanbanColumn.split("-")[1]
    );

    if (us.column === targetUsTypeColumn) return;

    const isScrumMaster = currentMember.roles.includes('Scrum Master');
    if (isScrumMaster) {
      us.column = targetUsTypeColumn;
      updateUsColumn(usId, targetUsTypeColumn);
      return;
    }

    // Verificamos si la us tiene una tarea dentro de la columna a la que se esta moviendo
    us.tasks = []; //TODO: Obtener las tareas de la US
    const hasTask =
      us.tasks.some((task) => task.column === usTypeColumn) || us.column === 0;

    // Verificamos si el usuario que quiere mover la us es el mismo que esta asignado a la us
    const isAssigned = us.user?.id === currentMember.id;

    // Verificamos si se esta moviendo a una columna anterior a la actual
    const isBacking = us.column > targetUsTypeColumn;

    if (isAssigned && (hasTask || isBacking)) {
      us.column = targetUsTypeColumn;
      updateUsColumn(usId, targetUsTypeColumn);
    } else restoreUs(us);
  },
});

function restoreUs(us) {
  Swal.fire({
    title: "No puedes mover esta US",
    icon: "error",
    showClass: {
      backdrop: "swal2-noanimation", // disable backdrop animation
      icon: "", // disable icon animation
    },
    confirmButtonText: "Ok",
  });
  const kanbanUsId = `us-${us.id}`;
  kanban.removeElement(kanbanUsId);
  const originalColumn = activeUsType.columns[us.column];
  kanban.addElement(`board-${originalColumn}`, {
    id: kanbanUsId,
    title: getUsTemplate(us.id, us),
  });
}
/**
 * Obtiene todas las US de un tipo y columna
 * @param {number} usTypeId Id del tipo de US
 * @param {number} indexColumn Indice de la columna dentro de columns del tipo de US
 * @returns {Array} Lista de US
 */
function getUsByType(usTypeId, indexColumn) {
  return user_stories
    .filter((us) => us.us_type === usTypeId && us.column === indexColumn)
    .map(({ id, ...usData }) => ({
      id: `us-${id}`,
      title: getUsTemplate(id, usData),
    }));
}

function getUsTemplate(id, us) {
  console.log(us);
  const htmlTemplate = `
    <div class="kanban-item-title">
      ${us.title}
    </div>
    <div class="kanban-item-footer">
      <p class="kanban-item-code">${us.code}</p>
      <div class="kanban-item-footer__right">
        <span class="badge rounded-pill text-bg-dark">${
          us.sprint_priority
        }</span>
        ${
          us.user
            ? ` <img src="${us.user.picture}" alt="" width="24" height="24" class="rounded-circle">`
            : ""
        }
        <a href="/projects/${
          us.project
        }/backlog/${id}/" class="kanban-item-add btn px-1 py-0" title="Informacion extra" onclick="redirectToViewAdd(${id}, ${
    us.project
  })">
            <span class=""><i class="fa fa-list-alt" aria-hidden="true"></i>
            </span>
        </a>
        <a href="/projects/${
          us.project
        }/backlog/${id}/tasks/create" class="kanban-item-add btn px-1 py-0" title="Agregar Tarea" onclick="redirectToViewAddTask(${id}, ${
    us.project
  })">
            <span class=""><i class="fa fa-plus-square" aria-hidden="true"></i>
            </span>
        </a>
      </div>
    </div>`;

  return htmlTemplate;
}

function redirectToViewAdd(us_id, project_id) {
  window.location = (`/projects/${project_id}/backlog/${us_id}/`);
}

function redirectToViewAddTask(us_id, project_id) {
  window.location = (`/projects/${project_id}/backlog/${us_id}/tasks/create`);
}

function createBoard(usType) {
  return usType.columns.map((column, index) => ({
    id: `board-${column}`,
    title: column,
    item: getUsByType(usType.id, index),
    dragTo: usType.columns
      .filter((c) => c !== column)
      .map((column) => `board-${column}`),
  }));
}
/**
 * Funcion que se ejecuta al seleccionar un tipo de US, actualiza el tablero
 */
function filterUs() {
  // Obtener el tipo de US seleccionado
  const usType = document.getElementById("us_type").value;
  activeUsType = us_types.find((us) => us.id === parseInt(usType));

  // Actualizar el tablero
  const boards = createBoard(activeUsType);

  // Eliminar las columnas del tablero actual
  const currentBoardIds = currentBoards.map((board) => board.id);
  currentBoardIds.forEach((boardId) => {
    kanban.removeBoard(boardId);
  });

  // Agregar las columnas del nuevo tablero
  kanban.addBoards(boards);
  currentBoards = boards;
}

async function updateUsColumn(usId, column) {
  const url = `/projects/${projectId}/user-stories/${usId}/`;
  const csrftoken = document.cookie
    .split(";")
    .find((row) => row.trim().startsWith("csrftoken="))
    .split("=")[1]
    .trim();

  fetch(url, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": csrftoken,
    },
    body: JSON.stringify({ column }),
  })
    .then((response) => response.json())
    .then((data) => {
      console.log("Success:", data);
    })
    .catch((error) => {
      console.error("Error:", error);
    });
}
